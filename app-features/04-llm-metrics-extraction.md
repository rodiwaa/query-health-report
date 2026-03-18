# LLM Health Metrics Extraction

## Overview
Sends parsed markdown to a DeepSeek LLM via LiteLLM to extract structured health test results as JSON.

## Location
`main.py` — `json_node` (lines 102–148)

## What It Does
- Constructs a prompt requesting structured JSON output from the parsed sections
- Calls `deepseek/deepseek-chat` via LiteLLM (2000 token limit)
- Parses the LLM response into a validated JSON object
- Recovers from truncated responses using regex fallback

## Output JSON Schema
```json
{
  "collection_date": "DD-MM-YY",
  "tests": [
    {
      "name": "TEST_NAME",
      "value": 44.0,
      "unit": "mg/dL",
      "ref_min": 40,
      "ref_max": 60
    }
  ]
}
```

## Key Details
- Model configured via `LLM_MODEL` env var (default: `deepseek/deepseek-chat`)
- Detects collection date from phrases: "blood collected on", "sample date", "collection date"
- Truncation recovery: uses regex `\{[^{}]*"name"[^{}]*\}` to salvage partial arrays
