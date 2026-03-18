# Report Persistence

## Overview
Saves extracted health metrics as a versioned JSON file in the `.reports/` directory.

## Location
`main.py` — `save_node` (lines 151–160)

## What It Does
- Creates `.reports/` directory if it doesn't exist
- Writes the extracted health JSON to `.reports/<YYYY-MM-DDTHH-MM>.json`
- Uses ISO timestamp in the filename to ensure uniqueness and chronological ordering
- Pretty-prints JSON with 2-space indentation

## Example Output
```
.reports/2026-03-18T20-10.json
```

These files are the persistent data store for all query and trend features.
