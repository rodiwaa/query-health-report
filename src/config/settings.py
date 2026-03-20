"""All constants and environment variables for the health report pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.home() / ".env" / ".env")

# LangSmith project
os.environ["LANGSMITH_PROJECT"] = "claude-health-report-trends-uploads"

# LLM models
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
INTENT_MODEL = os.getenv("INTENT_MODEL", "groq/llama-3.1-8b-instant")
# FIXME: fixing latency — use Groq for fast JSON extraction instead of DeepSeek
EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "groq/llama-3.3-70b-versatile")

# Paths
REPORT_PATH = os.getenv("REPORT_PATH", "")
REPORTS_DIR = Path(".reports")
TRENDS_OUTPUT = Path("health_trends.html")
