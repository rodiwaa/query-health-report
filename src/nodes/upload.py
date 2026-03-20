"""Upload node — validate file exists and record its path."""

from pathlib import Path

from src.graph.state import State


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
