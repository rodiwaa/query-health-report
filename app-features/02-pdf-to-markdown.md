# PDF to Markdown Conversion

## Overview
Converts an uploaded PDF health report into markdown text using the Docling library.

## Location
`main.py` — `markdown_node` (lines 70–79)

## What It Does
- Uses `docling.document_converter.DocumentConverter` to parse the PDF
- Exports the result as markdown via `.export_to_markdown()`
- Handles mixed content: unstructured text, tables, and formatted sections
- Logs character count of the produced markdown

## Notes
- Docling downloads ML models on first run — expect a slow cold start (10–30s)
- Output markdown is passed to the parse node for section splitting
