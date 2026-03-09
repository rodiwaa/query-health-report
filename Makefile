install:
	uv venv .venv
	uv pip install -r requirements.txt --python .venv/bin/python3

run:
	.venv/bin/python3 main.py

run-ui:
	.venv/bin/chainlit run chainlit_app.py
