from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class HelloState(TypedDict):
    name: str
    greeting: str


def build_greeting(state: HelloState) -> HelloState:
    name = state.get("name", "").strip() or "world"
    return {"name": name, "greeting": f"Hello, {name}!"}


def build_graph():
    graph = StateGraph(HelloState)
    graph.add_node("build_greeting", build_greeting)
    graph.add_edge(START, "build_greeting")
    graph.add_edge("build_greeting", END)
    return graph.compile()


def run(name: str = "world") -> str:
    app = build_graph()
    result = app.invoke({"name": name, "greeting": ""})
    return result["greeting"]


if __name__ == "__main__":
    print(run("LangGraph"))
