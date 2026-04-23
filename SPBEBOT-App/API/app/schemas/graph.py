from __future__ import annotations

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    category: str
    description: str
    size: float = 1.0
    color: str


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str


class GraphPayload(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    stats: dict[str, int]


class GraphSearchResponse(BaseModel):
    query: str
    graph: GraphPayload
    related_items: list[dict[str, str | float]]


class GraphStats(BaseModel):
    total_nodes: int
    total_edges: int
    domains: int
    aspects: int
    indicators: int
    max_full_graph_nodes: int
