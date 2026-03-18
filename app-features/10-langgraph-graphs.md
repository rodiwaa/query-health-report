# LangGraph Graphs & State

## Overview
Two compiled LangGraph state machines power the application — one for the upload pipeline, one for querying.

## Location
`main.py` — lines 341–369

## State Model
```python
class State(BaseModel):
    messages: list        # add_messages reducer
    file_path: str
    raw_markdown: str
    parsed_data: dict
    health_json: dict
```

## Upload Pipeline Graph
```
START → upload_node → markdown_node → parse_node → json_node → save_node → save_notion_node → trend_node → END
```

## Query Graph (separate)
```
START → query_node → END
```

## Compiled Instances
- `app` — upload pipeline
- `query_app` — query interface

Both are imported and invoked by `chainlit_app.py`.
