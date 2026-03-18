# Trend Chart Generation

## Overview
Aggregates all historical reports and generates an interactive HTML line chart showing health metrics over time.

## Location
`main.py` — `trend_node` (lines 186–313)

## What It Does
- Reads all `.reports/*.json` files in chronological order
- Builds a time-series dataset for every health metric across all reports
- Generates `health_trends.html` — a self-contained interactive chart

## Chart Details
- Library: React + Chart.js (loaded via CDN)
- Title: "Health Metrics Over Time"
- Subtitle: report count and metric count
- One line per metric, 10-colour palette
- Dates formatted as `DD-MONTHNAME-YYYY` (e.g. `19-OCTOBER-2024`)
- Sorted chronologically (not alphabetically)
- Supports null values across reports (`spanGaps: true`)

## Key Implementation Notes
- Metric keys are normalised to lowercase for consistent grouping
- Warns if the same metric has different units across reports
- Re-generated on every pipeline run (full refresh)

## Current Data
- 5 reports loaded
- 10 metrics tracked: Total Cholesterol, HDL, LDL, Triglycerides, TC/HDL, TRIG/HDL, LDL/HDL, HDL/LDL, Non-HDL, VLDL
