"""Date formatting utilities."""

from datetime import datetime


def format_date_label(raw: str) -> str:
    """Parse DD-MM-YY date string and return DD-MONTHNAME-YYYY (e.g. 30-JUNE-2024)."""
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%-d-%B-%Y").upper()
        except ValueError:
            continue
    return raw
