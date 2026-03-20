"""Query graph: single query_node that answers health questions."""

from langgraph.graph import END, START, StateGraph

from src.graph.state import State
from src.nodes.query import query_node

query_graph = StateGraph(State)
query_graph.add_node("query", query_node)
query_graph.add_edge(START, "query")
query_graph.add_edge("query", END)

query_app = query_graph.compile()
