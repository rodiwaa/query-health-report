"""Chainlit UI for health report upload and metric extraction."""

import asyncio
import os
import tempfile
from pathlib import Path

import chainlit as cl
from langchain_core.messages import HumanMessage
from litellm import completion

from main import TRENDS_OUTPUT, app, query_app

INTENT_MODEL = os.getenv("INTENT_MODEL", "groq/llama-3.1-8b-instant")


def classify_intent(text: str) -> str:
    """Returns 'upload' or 'query' using a fast Groq model."""
    prompt = (
        "Classify this user message as exactly one word: 'upload' or 'query'.\n"
        "'upload' = user wants to upload or add a health report.\n"
        "'query' = user is asking a question about their health data.\n"
        f"Message: {text}\nAnswer:"
    )
    response = completion(model=INTENT_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=5)
    label = response.choices[0].message.content.strip().lower()
    return "upload" if "upload" in label else "query"


@cl.action_callback("open_charts")
async def on_open_charts(action: cl.Action):
    charts_path = action.payload.get("path", "")
    await cl.Message(content=f'<a href="file://{charts_path}" target="_blank">📊 Open Charts</a>').send()


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "Welcome to Health Trends!\n\n"
            "Upload a health report PDF and I will extract your metrics automatically.\n"
            "Use the paperclip icon to attach your file."
        )
    ).send()


@cl.on_message
async def on_message(msg: cl.Message):
    # File attached → always run upload pipeline
    if not msg.elements:
        intent = await asyncio.get_event_loop().run_in_executor(
            None, lambda: classify_intent(msg.content)
        )
        if intent == "upload":
            await cl.Message(content="Please attach a PDF health report to upload.").send()
            return

        # Query intent
        await cl.Message(content="Searching your health data...").send()
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: query_app.invoke({"messages": [HumanMessage(content=msg.content)]})
        )
        answer = result["messages"][-1].content
        await cl.Message(content=answer).send()
        return

    file_el = msg.elements[0]
    file_path = file_el.path

    status = cl.Message(content="Processing your report...")
    await status.send()

    tmp_path = None
    try:
        # Copy to a temp file with correct extension so docling can detect format
        suffix = Path(file_el.name).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(Path(file_path).read_bytes())

        await cl.Message(content="Converting to markdown...").send()

        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: app.invoke({"file_path": tmp_path})
        )

        tests = result.get("health_json", {}).get("tests", [])
        # Find the saved report path from messages
        saved_msg = next(
            (m.content for m in result["messages"] if "Saved report" in m.content),
            None,
        )

        summary_lines = [f"**Done!** Extracted **{len(tests)} metrics**."]
        if saved_msg:
            summary_lines.append(f"Report saved: `{saved_msg.split('Saved report to ')[-1]}`")
        if tests:
            sample = tests[:5]
            rows = ["| Metric | Value | Unit |", "|--------|-------|------|"]
            for t in sample:
                rows.append(f"| {t.get('name','')} | {t.get('value','')} | {t.get('unit','')} |")
            if len(tests) > 5:
                rows.append(f"| ... and {len(tests) - 5} more | | |")
            summary_lines.append("\n" + "\n".join(rows))

        await cl.Message(content="\n".join(summary_lines)).send()

        charts_path = Path(TRENDS_OUTPUT).resolve()
        await cl.Message(
            content="",
            actions=[
                cl.Action(
                    name="open_charts",
                    label="📊 Open Charts",
                    payload={"path": str(charts_path)},
                )
            ],
        ).send()

    except Exception as e:
        await cl.Message(content=f"Error processing report: {e}").send()
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
