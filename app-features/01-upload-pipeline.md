# Upload Pipeline

## Overview
Validates and registers an uploaded health report file before processing begins.

## Location
`main.py` — `upload_node` (lines 56–67)

## What It Does
- Accepts a file path from the LangGraph state
- Validates the file exists on disk
- Passes the path downstream for PDF conversion
- Emits a status log: `[upload] Uploaded: <filename>`

## Error Handling
Raises `FileNotFoundError` if the file path is invalid.
