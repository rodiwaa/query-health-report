"""CLI entry point — runs the upload pipeline on a single report."""

import json

from src.config.settings import REPORT_PATH
from src.graph.pipeline import app
from src.graph.query import query_app  # noqa: F401  (re-exported for chainlit_app)

if __name__ == "__main__":
    result = app.invoke({"file_path": REPORT_PATH})
    print("\n── Summary ──")
    for msg in result["messages"]:
        print(f"  {msg.content}")
    print(f"\nHealth JSON:\n{json.dumps(result['health_json'], indent=2)}")
