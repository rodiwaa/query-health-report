"""Parse node — parse markdown into structured sections."""

from src.graph.state import State


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
