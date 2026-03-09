# Project Description — claude-health-trends-upload

## What This Project Does

A LangGraph pipeline that processes uploaded health report PDFs, extracts lab metrics using an LLM, saves them as versioned JSON, and renders a trend chart HTML.

A Chainlit web UI allows users to upload files directly in the browser instead of referencing a file path.

---

## Pipeline (main.py)

LangGraph `StateGraph` with these nodes in order:

```
upload → markdown → parse → json → save → trend
```

| Node | What it does |
|------|-------------|
| `upload_node` | Validates file exists, records path |
| `markdown_node` | Converts PDF to markdown via `docling` |
| `parse_node` | Splits markdown into sections by heading |
| `json_node` | Sends content to LLM (DeepSeek via LiteLLM), extracts metrics as JSON |
| `save_node` | Saves JSON to `.reports/<timestamp>.json` |
| `trend_node` | Reads all `.reports/*.json`, generates `health_trends.html` with Chart.js |

**LLM**: `deepseek/deepseek-chat` via LiteLLM (set in `.env` as `LLM_MODEL`)

**State model**: Pydantic `BaseModel` (not TypedDict) — fields: `messages`, `file_path`, `raw_markdown`, `parsed_data`, `health_json`

---

## Chainlit UI (chainlit_app.py)

- `on_chat_start`: sends welcome message
- `on_message`: handles file attachment → copies to temp file → runs pipeline → shows metric summary table → cleans up temp file
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

### CRITICAL: Do not use `uv run` or `uv add` for this project

This project lives inside a monorepo workspace (`rodi-lg-projs`). The workspace root has `mlx-lm` which conflicts with `docling` (`huggingface-hub` version clash). `uv run` and `uv add` resolve the whole workspace and will fail.

**Always use the local `.venv` directly:**

```bash
uv pip install <package> --python .venv/bin/python3   # install packages
.venv/bin/python3 main.py                             # run scripts
.venv/bin/chainlit run chainlit_app.py                # run chainlit
```

`uv add --frozen` also failed. Stick to `uv pip install --python .venv/bin/python3`.

### Key packages in .venv
- `docling` — PDF to markdown conversion (heavy, downloads ML models on first run)
- `chainlit` — web UI
- `langgraph` — graph orchestration
- `litellm` — LLM calls
- `langsmith` — tracing (auto-enabled via env vars, no extra install needed)

---

## Behaviour Rules

- **No unnecessary changes.** Only modify exactly what was asked. Do not refactor surrounding code, rename variables, add error handling, or "improve" adjacent logic while implementing a requested change.

---

## Known Issues / Lessons Learned

1. **First upload shows no messages** — Fixed by wrapping `app.invoke()` in `run_in_executor`. Root cause: docling + LLM call blocks the async event loop for 10-30s on first run (model init). Without the executor, Chainlit can't flush messages to the browser until the entire handler returns.

2. **`uv add docling` fails at workspace level** — See dependency notes above. Use `uv pip install` with explicit `--python` flag pointing to `.venv`.

3. **LLM response truncation** — DeepSeek sometimes truncates JSON mid-array. `json_node` has a regex fallback that recovers complete test objects from the partial response.

4. **Chainlit file path** — `msg.elements[0].path` gives the temp path Chainlit stores the upload. Copy it to your own temp file with the correct extension (`.pdf`) before passing to docling, otherwise format detection may fail.

---

## File Map

```
main.py              — LangGraph pipeline + graph definition
chainlit_app.py      — Chainlit web UI
Makefile             — run / run-ui / install targets
pyproject.toml       — project metadata (uv managed)
.env                 — API keys (never commit)
.reports/            — versioned JSON outputs per report
health_trends.html   — generated trend chart
CLAUDE.md            — project rules and development phases
project-desc.md      — this file
```

---

## Next / Planned Features

- Query interface: user asks natural language questions about their metric history (e.g. "how has my cholesterol changed?") — rule-based in next phase, LLM-powered later
