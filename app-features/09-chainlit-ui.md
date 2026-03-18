# Chainlit Web UI

## Overview
A web chat interface that handles file uploads, runs the pipeline, and allows querying — all from the browser.

## Location
`chainlit_app.py` — full file

## Features

### Intent Classification
- Model: `groq/llama-3.1-8b-instant` (fast, 5 tokens max)
- Classifies user message as `"upload"` or `"query"`
- Non-upload messages default to `"query"`
- Configured via `INTENT_MODEL` env var

### File Upload Flow
1. User attaches a PDF via the paperclip icon
2. File is copied to a temp path with `.pdf` extension (required for Docling)
3. Full pipeline runs via `app.invoke({"file_path": tmp_path})`
4. UI displays:
   - Extracted metric count
   - Table of first 5 metrics (Metric | Value | Unit)
   - "... and X more" if over 5 metrics
   - "Open Charts" action button linking to `health_trends.html`
5. Temp file is cleaned up

### Query Flow
- User types a health question
- Intent classified as `"query"`
- Routed to `query_app` graph
- LLM answer displayed in chat

### Welcome Message
Shown on chat start — instructs user to use the paperclip icon to upload a report.

### Async Handling
Pipeline runs in `asyncio.run_in_executor()` to prevent blocking the Chainlit event loop during Docling's slow initialisation.

## Run
```
make run-ui
```
