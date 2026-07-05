"""Pipeline compilation shared by all agents.

Every agent defines its workflow as an ordered list of named async node
functions ``(state) -> state``. ``compile_pipeline`` builds a LangGraph
``StateGraph`` when langgraph is installed, and otherwise returns a plain
sequential runner with the same ``ainvoke`` interface — so the agent system
works identically with or without the dependency.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Sequence

logger = logging.getLogger("nexus.agents")

NodeFn = Callable[[dict], Awaitable[dict]]


class SequentialPipeline:
    """Minimal LangGraph-compatible runner: nodes executed in order."""

    def __init__(self, name: str, nodes: Sequence[tuple[str, NodeFn]]) -> None:
        self.name = name
        self.nodes = list(nodes)

    async def ainvoke(self, state: dict) -> dict:
        """Run every node in order, threading the state dict through."""
        for node_name, fn in self.nodes:
            try:
                update = await fn(state)
                if update:
                    state.update(update)
            except Exception as exc:  # noqa: BLE001 — route to human review
                logger.exception("%s: node %s failed", self.name, node_name)
                state.setdefault("errors", []).append(
                    {"agent": self.name, "node": node_name, "error": str(exc)}
                )
        return state


def compile_pipeline(name: str, nodes: Sequence[tuple[str, NodeFn]]) -> Any:
    """Compile nodes into a LangGraph StateGraph, or a sequential fallback.

    Both return values expose ``await pipeline.ainvoke(state)``.
    """
    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(dict)
        for node_name, fn in nodes:
            # StateGraph(dict) has no per-key channels to merge on, so
            # LangGraph treats whatever a node returns as the ENTIRE new
            # state, silently dropping keys (like "db" and "org_id") that the
            # node didn't re-emit. Wrap every node so it always returns the
            # full state (incoming state merged with its own partial update),
            # matching SequentialPipeline's in-place `state.update()` behavior.
            def make_wrapped(node_fn: NodeFn) -> NodeFn:
                async def wrapped(state: dict) -> dict:
                    update = await node_fn(state)
                    return {**state, **(update or {})}

                return wrapped

            graph.add_node(node_name, make_wrapped(fn))
        node_names = [n for n, _ in nodes]
        graph.set_entry_point(node_names[0])
        for current, nxt in zip(node_names, node_names[1:]):
            graph.add_edge(current, nxt)
        graph.add_edge(node_names[-1], END)
        return graph.compile()
    except Exception:  # noqa: BLE001 — langgraph missing or incompatible
        logger.info("%s: langgraph unavailable, using sequential pipeline", name)
        return SequentialPipeline(name, nodes)
