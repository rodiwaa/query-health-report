"""MCP server: exposes save_to_notion(health_json) tool."""
import os
from datetime import datetime
import httpx
from mcp.server.fastmcp import FastMCP

NOTION_TOKEN = os.environ["NOTION_API_KEY"]
NOTION_DB_ID = "324ad8c23036801286b6c8c322085bd4"
NOTION_VERSION = "2022-06-28"

mcp = FastMCP("notion-health-saver")


def _parse_date(raw: str) -> str | None:
    """Convert DD-MM-YY to YYYY-MM-DD for Notion."""
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


@mcp.tool()
def save_to_notion(health_json: dict) -> str:
    """Save all tests from health_json as rows in the Notion database."""
    tests = health_json.get("tests", [])
    notion_date = _parse_date(health_json.get("collection_date", ""))
    created, errors = 0, []

    with httpx.Client() as client:
        for test in tests:
            props = {
                "Name": {"title": [{"text": {"content": test.get("name", "")}}]},
                "Value": {"number": test.get("value")},
                "Unit": {"rich_text": [{"text": {"content": str(test.get("unit", ""))}}]},
            }
            if notion_date:
                props["Date"] = {"date": {"start": notion_date}}
            if test.get("ref_min") is not None:
                props["Ref Min"] = {"number": test["ref_min"]}
            if test.get("ref_max") is not None:
                props["Ref Max"] = {"number": test["ref_max"]}
            payload = {
                "parent": {"database_id": NOTION_DB_ID},
                "properties": props,
            }
            resp = client.post("https://api.notion.com/v1/pages", headers=_headers(), json=payload)
            if resp.status_code == 200:
                created += 1
            else:
                errors.append(f"{test.get('name')}: {resp.status_code} {resp.text[:120]}")

    return f"Created {created} rows." if not errors else f"Created {created} rows. Errors: {'; '.join(errors)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
