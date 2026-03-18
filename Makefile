install:
	uv venv .venv
	uv pip install -r requirements.txt --python .venv/bin/python3

run:
	.venv/bin/python3 main.py

run-ui:
	uv run chainlit run chainlit_app.py

run-notion-mcp:
	.venv/bin/python3 mcp/notion_mcp.py
