from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.graph import GraphPayload, GraphSearchResponse, GraphStats
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])
service = GraphService()


@router.get("", response_model=GraphPayload)
def get_graph(
    full: bool = Query(False, description="Return full graph payload"),
    indicators_per_aspect: int = Query(3, ge=1, le=20),
) -> GraphPayload:
    if full:
        return GraphPayload(**service.export_graph())
    return GraphPayload(**service.export_overview_graph(indicators_per_aspect=indicators_per_aspect))


@router.get("/search", response_model=GraphSearchResponse)
def search_graph(q: str = Query(..., min_length=2)) -> GraphSearchResponse:
    return GraphSearchResponse(**service.search(q))


@router.get("/stats")
def get_graph_stats() -> dict:
    """Endpoint ringan: hanya statistik, tanpa data node/edge."""
    return service.get_stats()
