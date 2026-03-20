"""Trend node — load all versioned reports and render health_trends.html."""

import json
import warnings

from src.config.settings import REPORTS_DIR, TRENDS_OUTPUT
from src.graph.state import State
from src.utils.dates import format_date_label


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
    all_labels_set.sort()

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
