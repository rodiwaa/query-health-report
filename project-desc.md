# Project Description — claude-health-trends-upload

## What This Project Does

A LangGraph pipeline that processes uploaded health report PDFs, extracts lab metrics using an LLM, saves them as versioned JSON, and renders a trend chart HTML.

A Chainlit web UI allows users to upload files directly in the browser instead of referencing a file path.

---

## Pipeline (main.py)

LangGraph `StateGraph` with these nodes in order:

```
upload → markdown → parse → json → save → save_notion → trend
```

| Node | What it does |
|------|-------------|
| `upload_node` | Validates file exists, records path |
| `markdown_node` | Converts PDF to markdown via `docling` |
| `parse_node` | Splits markdown into sections by heading |
| `json_node` | Sends content to LLM (DeepSeek via LiteLLM), extracts metrics as JSON |
| `save_node` | Saves JSON to `.reports/<timestamp>.json` |
| `save_notion_node` | Calls Notion MCP server to push metrics to Notion database |
| `trend_node` | Reads all `.reports/*.json`, generates `health_trends.html` with Chart.js |

**LLM**: `deepseek/deepseek-chat` via LiteLLM (set in `.env` as `LLM_MODEL`)

**State model**: Pydantic `BaseModel` (not TypedDict) — fields: `messages`, `file_path`, `raw_markdown`, `parsed_data`, `health_json`

---

## Chainlit UI (chainlit_app.py)

- `on_chat_start`: sends welcome message
- `on_message`: classifies intent (`upload` vs `query`) via Groq Llama 3.1 8B (5 tokens, fast)
  - **upload intent + file attached**: copies to temp file → runs upload pipeline → shows metric summary table + "Open Charts" button → cleans up temp file
  - **query intent**: runs `query_app` graph → LLM answers from `.reports/*.json` context
  - **upload intent + no file**: prompts user to attach a PDF
- Pipeline is run via `asyncio.get_event_loop().run_in_executor(None, ...)` — **critical**: must be async/threaded or first-upload messages won't render (Chainlit event loop blocks on sync `app.invoke()`)

---

## Data Storage

- **Reports**: `.reports/<YYYY-MM-DDTHH-MM>.json` — each file is one processed report
- **Trend chart**: `health_trends.html` — regenerated on every pipeline run
- **Raw files**: never stored — temp file is deleted after processing

---

## Running the Project

```bash
make run       # CLI mode: processes REPORT_PATH from .env
make run-ui    # Chainlit web UI at http://localhost:8000
```

---

## Telemetry

LangSmith tracing is active. Project name: `claude-health-report-trends-uploads`

Config in `.env`:
```
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

Project name is overridden in `main.py` at startup:
```python
os.environ["LANGSMITH_PROJECT"] = "claude-health-report-trends-uploads"
```

---

## Dependency / Environment Notes — Read Before Adding Packages

### CRITICAL: Do not use `uv add` for this project

This project lives inside a monorepo workspace (`rodi-lg-projs`). The workspace root has `mlx-lm` which conflicts with `docling` (`huggingface-hub` version clash). `uv add` resolves the whole workspace and will fail.

**For installing packages, always use:**

```bash
uv pip install <package> --python .venv/bin/python3   # install packages
```

**For running scripts and tools, `uv run` works correctly** — it uses the local `.venv` without workspace resolution:

```bash
uv run python main.py                  # run scripts
uv run chainlit run chainlit_app.py    # run chainlit (used in Makefile)
```

`uv add --frozen` also failed. Stick to `uv pip install --python .venv/bin/python3` for installs.

### Key packages in .venv
- `docling` — PDF to markdown conversion (heavy, downloads ML models on first run)
- `chainlit` — web UI
- `langgraph` — graph orchestration
- `litellm` — LLM calls
- `langsmith` — tracing (auto-enabled via env vars, no extra install needed)
- `mcp` — MCP stdio client/server for Notion integration

---

## Behaviour Rules

- **No unnecessary changes.** Only modify exactly what was asked. Do not refactor surrounding code, rename variables, add error handling, or "improve" adjacent logic while implementing a requested change.

---

## Known Issues / Lessons Learned

1. **First upload shows no messages** — Fixed by wrapping `app.invoke()` in `run_in_executor`. Root cause: docling + LLM call blocks the async event loop for 10-30s on first run (model init). Without the executor, Chainlit can't flush messages to the browser until the entire handler returns.

2. **`uv add docling` fails at workspace level** — See dependency notes above. Use `uv pip install` with explicit `--python` flag pointing to `.venv`.

3. **LLM response truncation** — DeepSeek sometimes truncates JSON mid-array. `json_node` has a regex fallback that recovers complete test objects from the partial response.

4. **Chainlit file path** — `msg.elements[0].path` gives the temp path Chainlit stores the upload. Copy it to your own temp file with the correct extension (`.pdf`) before passing to docling, otherwise format detection may fail.

5. **Query path silent failures** — The original query path had no try/except, so errors were silently swallowed and no response was shown. Always wrap both intent classification and graph invocation in try/except in `chainlit_app.py`.

6. **Intent classification failure** — If the intent model call fails, fall back to `"query"` intent rather than crashing.

7. **Trend chart date sorting** — Date labels were sorting alphabetically instead of chronologically. Fixed by parsing `DD-MONTHNAME-YYYY` labels with a `parse_label_date` key function before sorting.

8. **`uv run` works for running, not for adding packages** — `uv run chainlit run ...` correctly uses the local `.venv`. Only `uv add` triggers workspace-level resolution and fails. Makefile now uses `uv run chainlit run chainlit_app.py`.

---

## File Map

```
main.py              — LangGraph pipeline + graph definition
chainlit_app.py      — Chainlit web UI
mcp/notion_mcp.py    — Notion MCP stdio server
Makefile             — run / run-ui / install / run-notion-mcp targets
pyproject.toml       — project metadata (uv managed)
.env                 — API keys (never commit)
.reports/            — versioned JSON outputs per report
health_trends.html   — generated trend chart
app-features/        — feature documentation (one file per feature)
CLAUDE.md            — project rules and development phases
project-desc.md      — this file
```

---

## Next / Planned Features

- Phase 3 refactor: restructure into `src/graph/`, `src/nodes/`, `src/utils/`
- Phase 4: Qdrant vector database integration (replace `.reports/` JSON files)
