"""Main upload pipeline graph: upload → markdown → parse → json → save → trend."""

from langgraph.graph import END, START, StateGraph

from src.graph.state import State
from src.nodes.json_extract import json_node
from src.nodes.markdown import markdown_node
from src.nodes.parse import parse_node
from src.nodes.save import save_node
from src.nodes.trend import trend_node
from src.nodes.upload import upload_node

graph = StateGraph(State)
graph.add_node("upload", upload_node)
graph.add_node("markdown", markdown_node)
graph.add_node("parse", parse_node)
graph.add_node("json", json_node)
graph.add_node("save", save_node)
graph.add_node("trend", trend_node)

graph.add_edge(START, "upload")
graph.add_edge("upload", "markdown")
graph.add_edge("markdown", "parse")
graph.add_edge("parse", "json")
graph.add_edge("json", "save")
graph.add_edge("save", "trend")
graph.add_edge("trend", END)

app = graph.compile()
