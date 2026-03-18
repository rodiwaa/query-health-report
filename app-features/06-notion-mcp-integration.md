# Notion MCP Integration

## Overview
An MCP (Model Context Protocol) stdio server that pushes extracted health metrics to a Notion database.

## Location
`mcp/notion_mcp.py` — full file
`main.py` — `save_notion_node` (lines 163–183)

## What It Does
- Exposes a `save_to_notion(health_json: dict)` MCP tool
- Creates one Notion database row per test result
- Maps extracted fields to Notion properties

## Notion Properties Created Per Row
| Property | Type | Source |
|----------|------|--------|
| Name | Title | `test["name"]` |
| Value | Number | `test["value"]` |
| Unit | Text | `test["unit"]` |
| Date | Date | `collection_date` (converted DD-MM-YY → YYYY-MM-DD) |
| Ref Min | Number | `test["ref_min"]` |
| Ref Max | Number | `test["ref_max"]` |

## Configuration
- `NOTION_API_KEY` — API key from `.env`
- `NOTION_DB_ID` — Target database ID (`324ad8c23036801286b6c8c322085bd4`)
- Notion API version: `2022-06-28`

## Run Standalone
```
make run-notion-mcp
```
