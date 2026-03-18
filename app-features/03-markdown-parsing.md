# Markdown Section Parsing

## Overview
Splits the raw markdown output into named sections for structured downstream processing.

## Location
`main.py` — `parse_node` (lines 82–99)

## What It Does
- Scans markdown line by line
- Treats lines starting with `#` as section headings
- Groups all following content lines under that heading
- Normalises section names to `lowercase_with_underscores`

## Output Structure
```python
{
  "general": ["line1", "line2"],
  "lipids": ["hdl: 44 mg/dL", ...],
  "glucose": ["fasting: 95 mg/dL", ...]
}
```

The resulting dict is passed to the LLM extraction node.
