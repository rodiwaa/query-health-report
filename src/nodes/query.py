"""Query node — answer user health questions from stored reports."""

import json

from litellm import completion

from src.config.settings import LLM_MODEL, REPORTS_DIR
from src.graph.state import State


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
