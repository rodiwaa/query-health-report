"""State definition for the health report pipeline."""

from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class State(BaseModel):
    messages: Annotated[list, add_messages] = []
    file_path: str = ""
    raw_markdown: str = ""
    parsed_data: dict = {}
    health_json: dict = {}
