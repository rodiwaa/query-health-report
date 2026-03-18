# Health Data Query Interface

## Overview
Answers natural-language questions about stored health metrics using an LLM with all report data as context.

## Location
`main.py` — `query_node` (lines 316–336)

## What It Does
- Reads all `.reports/*.json` files and merges them into a single JSON context
- Sends the merged data + user question to the LLM
- Returns a concise, data-grounded answer
- Instructed to answer only from available data (no hallucination)

## Configuration
- Model: `LLM_MODEL` env var (default: `deepseek/deepseek-chat`)
- Max tokens: 500

## Example Queries
- "What is my latest LDL?"
- "How has my cholesterol changed over the last 3 months?"
- "Is my HDL within reference range?"

## Graph
Runs on a separate LangGraph instance (`query_app`) — independent of the upload pipeline.
