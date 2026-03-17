"""Phase 2 — Basic Graph: upload → markdown → parse → json → save → trend."""

import asyncio
import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from docling.document_converter import DocumentConverter
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from litellm import completion
from pydantic import BaseModel

load_dotenv(os.path.expanduser("~/.env/.env"))


def format_date_label(raw: str) -> str:
    """Parse DD-MM-YY date string and return DD-MONTHNAME-YYYY (e.g. 30-JUNE-2024)."""
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%-d-%B-%Y").upper()
        except ValueError:
            continue
    return raw


# Override LangSmith project name for this app
os.environ["LANGSMITH_PROJECT"] = "claude-health-report-trends-uploads"

# Config
REPORT_PATH = os.getenv("REPORT_PATH", "")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
REPORTS_DIR = Path(".reports")
TRENDS_OUTPUT = Path("health_trends.html")


# ── State ────────────────────────────────────────────────────────────────────

class State(BaseModel):
    messages: Annotated[list, add_messages] = []
    file_path: str = ""
    raw_markdown: str = ""
    parsed_data: dict = {}
    health_json: dict = {}


# ── Nodes ────────────────────────────────────────────────────────────────────

def upload_node(state: State) -> dict:
    """Validate the file exists and record its path."""
    if not state.file_path:
        raise ValueError("No file path provided.")
    path = Path(state.file_path)
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")
    print(f"[upload] loaded: {path}")
    return {
        "file_path": str(path),
        "messages": [{"role": "assistant", "content": f"Uploaded: {path.name}"}],
    }


def markdown_node(state: State) -> dict:
    """Convert the uploaded file to markdown using docling."""
    converter = DocumentConverter()
    result = converter.convert(state.file_path)
    markdown = result.document.export_to_markdown()
    print(f"[markdown] converted {len(markdown)} chars")
    return {
        "raw_markdown": markdown,
        "messages": [{"role": "assistant", "content": "Converted to markdown."}],
    }


def parse_node(state: State) -> dict:
    """Parse the markdown into structured sections."""
    lines = state.raw_markdown.splitlines()
    sections: dict[str, list[str]] = {}
    current = "general"

    for line in lines:
        if line.startswith("#"):
            current = line.lstrip("#").strip().lower().replace(" ", "_")
            sections[current] = []
        elif line.strip():
            sections.setdefault(current, []).append(line.strip())

    print(f"[parse] found sections: {list(sections.keys())}")
    return {
        "parsed_data": sections,
        "messages": [{"role": "assistant", "content": f"Parsed {len(sections)} sections."}],
    }


def json_node(state: State) -> dict:
    """Use LLM to extract health metrics from parsed markdown as structured JSON."""
    content = "\n".join(
        line for lines in state.parsed_data.values() for line in lines
    )
    prompt = (
        "Extract all health test results from the following medical report text. "
        "Return a JSON object with two keys: 'collection_date' and 'tests'. "
        "'collection_date' must be the date the blood was collected (look for phrases like 'blood collected on', 'sample date', 'collection date'), "
        "formatted as DD-MM-YY. If not found, set it to null. "
        "'tests' must be a list of objects, each with: 'name' (test name), 'value' (numeric observed value), "
        "'unit' (unit of measurement), 'ref_min' (lower bound of reference range, or null), "
        "'ref_max' (upper bound of reference range, or null). "
        "Return only valid JSON, no explanation.\n\n"
        f"{content}"
    )
    response = completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        health_json = json.loads(raw)
    except json.JSONDecodeError:
        # Response was truncated mid-JSON; recover complete test objects from the array
        import re
        matches = list(re.finditer(r'\{[^{}]*"name"[^{}]*\}', raw))
        tests = []
        for m in matches:
            try:
                tests.append(json.loads(m.group()))
            except json.JSONDecodeError:
                pass
        print(f"[json] response was truncated, recovered {len(tests)} tests")
        health_json = {"tests": tests}
    print(f"[json] extracted {len(health_json.get('tests', []))} tests")
    return {
        "health_json": health_json,
        "messages": [{"role": "assistant", "content": f"Extracted {len(health_json.get('tests', []))} test results."}],
    }


def save_node(state: State) -> dict:
    """Save health_json to .reports/<timestamp>.json."""
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    out_path = REPORTS_DIR / f"{timestamp}.json"
    out_path.write_text(json.dumps(state.health_json, indent=2))
    print(f"[save] saved to {out_path}")
    return {
        "messages": [{"role": "assistant", "content": f"Saved report to {out_path}."}],
    }


def save_notion_node(state: State) -> dict:
    """Send health_json to Notion via MCP stdio server."""
    async def _call():
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(Path(__file__).parent / "mcp" / "notion_mcp.py")],
            env={**os.environ},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("save_to_notion", {"health_json": state.health_json})
                return result.content[0].text

    try:
        summary = asyncio.run(_call())
        print(f"[save_notion] {summary}")
        return {"messages": [{"role": "assistant", "content": f"Notion: {summary}"}]}
    except Exception as exc:
        print(f"[save_notion] error (non-fatal): {exc}")
        return {"messages": [{"role": "assistant", "content": f"Notion save skipped: {exc}"}]}


def trend_node(state: State) -> dict:
    """Load all versioned reports and render health_trends.html with React + Chart.js."""
    report_files = sorted(REPORTS_DIR.glob("*.json"))
    if not report_files:
        print("[trend] no reports found")
        return {"messages": [{"role": "assistant", "content": "No reports for trend chart."}]}

    # Build metric timeline: { metric_key: [(label, value, unit), ...] }
    timeline: dict[str, list[tuple[str, float, str]]] = {}
    for report_file in report_files:
        data = json.loads(report_file.read_text())
        label = format_date_label(data.get("collection_date") or report_file.stem)
        for test in data.get("tests", []):
            key = test["name"].strip().lower()
            unit = test.get("unit", "")
            try:
                value = float(test["value"])
            except (TypeError, ValueError):
                continue
            if key not in timeline:
                timeline[key] = []
            # Warn on unit mismatch
            if timeline[key] and timeline[key][-1][2] != unit:
                warnings.warn(f"[trend] unit mismatch for '{key}': {timeline[key][-1][2]!r} vs {unit!r}")
            timeline[key].append((label, value, unit))

    # Build Chart.js datasets
    all_labels_set: list[str] = []
    for entries in timeline.values():
        for label, _, _ in entries:
            if label not in all_labels_set:
                all_labels_set.append(label)
    def parse_label_date(label: str):
        try:
            return datetime.strptime(label, "%-d-%B-%Y")
        except ValueError:
            return datetime.min

    all_labels_set.sort(key=parse_label_date)

    colors = [
        "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
        "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
    ]

    datasets = []
    for idx, (metric_key, entries) in enumerate(sorted(timeline.items())):
        entry_map = {lbl: val for lbl, val, _ in entries}
        unit = entries[-1][2] if entries else ""
        label_display = f"{metric_key} ({unit})" if unit else metric_key
        data_points = [entry_map.get(lbl, None) for lbl in all_labels_set]
        color = colors[idx % len(colors)]
        datasets.append({
            "label": label_display,
            "data": data_points,
            "borderColor": color,
            "backgroundColor": color,
            "pointRadius": 5,
            "spanGaps": True,
        })

    chart_data = {"labels": all_labels_set, "datasets": datasets}
    chart_data_json = json.dumps(chart_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Health Trends</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #f9fafb; color: #111; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 8px; }}
    p.subtitle {{ color: #666; margin-bottom: 24px; font-size: 0.9rem; }}
    .chart-container {{ background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); max-width: 1000px; }}
  </style>
</head>
<body>
  <div id="root"></div>
  <script>
    const CHART_DATA = {chart_data_json};

    function App() {{
      const canvasRef = React.useRef(null);

      React.useEffect(() => {{
        const ctx = canvasRef.current.getContext('2d');
        const chart = new Chart(ctx, {{
          type: 'line',
          data: CHART_DATA,
          options: {{
            responsive: true,
            plugins: {{
              legend: {{ display: false }},
              title: {{ display: true, text: 'Health Metrics Over Time', font: {{ size: 16 }} }},
            }},
            scales: {{
              x: {{ ticks: {{ display: true }}, title: {{ display: false }} }},
              y: {{ title: {{ display: true, text: 'Value' }} }},
            }},
          }},
        }});
        return () => chart.destroy();
      }}, []);

      return React.createElement('div', null,
        React.createElement('h1', null, 'Health Trends'),
        React.createElement('p', {{ className: 'subtitle' }}, `{len(report_files)} report(s) loaded · ${{CHART_DATA.datasets.length}} metric(s) tracked`),
        React.createElement('div', {{ className: 'chart-container' }},
          React.createElement('canvas', {{ ref: canvasRef }})
        )
      );
    }}

    ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
  </script>
</body>
</html>
"""

    TRENDS_OUTPUT.write_text(html)
    print(f"[trend] wrote {TRENDS_OUTPUT} ({len(timeline)} metrics, {len(report_files)} reports)")
    return {
        "messages": [{"role": "assistant", "content": f"Trend chart saved to {TRENDS_OUTPUT}."}],
    }


def query_node(state: State) -> dict:
    """Answer user health questions using stored .reports/*.json as context."""
    question = state.messages[-1].content
    reports = sorted(REPORTS_DIR.glob("*.json"))
    if not reports:
        return {"messages": [{"role": "assistant", "content": "No health reports found. Please upload a report first."}]}

    all_data = []
    for r in reports:
        data = json.loads(r.read_text())
        all_data.append({"file": r.stem, "tests": data.get("tests", [])})

    context = json.dumps(all_data, indent=2)
    prompt = (
        "You are a health assistant. Answer the user's question using only the data below.\n"
        f"Data (JSON, each entry is one health report by date):\n{context}\n\n"
        f"Question: {question}\nAnswer concisely and clearly."
    )
    response = completion(model=LLM_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=500)
    answer = response.choices[0].message.content
    return {"messages": [{"role": "assistant", "content": answer}]}


# ── Graph ────────────────────────────────────────────────────────────────────

graph = StateGraph(State)
graph.add_node("upload", upload_node)
graph.add_node("markdown", markdown_node)
graph.add_node("parse", parse_node)
graph.add_node("json", json_node)
graph.add_node("save", save_node)
graph.add_node("save_notion", save_notion_node)
graph.add_node("trend", trend_node)

graph.add_edge(START, "upload")
graph.add_edge("upload", "markdown")
graph.add_edge("markdown", "parse")
graph.add_edge("parse", "json")
graph.add_edge("json", "save")
graph.add_edge("json", "save_notion")
graph.add_edge("save", "trend")
graph.add_edge("save_notion", "trend")
graph.add_edge("trend", END)

app = graph.compile()


# ── Query Graph ───────────────────────────────────────────────────────────────

query_graph = StateGraph(State)
query_graph.add_node("query", query_node)
query_graph.add_edge(START, "query")
query_graph.add_edge("query", END)
query_app = query_graph.compile()


if __name__ == "__main__":
    result = app.invoke({"file_path": REPORT_PATH})
    print("\n── Summary ──")
    for msg in result["messages"]:
        print(f"  {msg.content}")
    print(f"\nHealth JSON:\n{json.dumps(result['health_json'], indent=2)}")
