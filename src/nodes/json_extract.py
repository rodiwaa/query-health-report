"""JSON extraction node — use LLM to extract health metrics as structured JSON."""

import json
import re

from litellm import completion

from src.config.settings import EXTRACTION_MODEL
from src.graph.state import State


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
    # FIXME: fixing latency — switched to Groq for faster inference, reduced max_tokens from 2000
    response = completion(
        model=EXTRACTION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
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
