"""Save node — persist health_json to .reports/<timestamp>.json."""

import json
from datetime import datetime

from src.config.settings import REPORTS_DIR
from src.graph.state import State


def save_node(state: State) -> dict:
    """Save health_json to .reports/<timestamp>.json."""
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = REPORTS_DIR / f"{timestamp}.json"
    out_path.write_text(json.dumps(state.health_json, indent=2))
    print(f"[save] saved to {out_path}")
    return {
        "messages": [{"role": "assistant", "content": f"Saved report to {out_path}."}],
    }
