"""
API routes for quantum execution queries.
Handles HTTP concerns only - business logic is in the service layer.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from neo4j.exceptions import ServiceUnavailable
from typing import Annotated

from app.graph.neo4j_store import Neo4jStore
from app.services.execution_query_service import ExecutionQueryService
from app.core.dependencies import get_neo4j_store

router = APIRouter(prefix="/api/executions", tags=["Executions"])

# ==================== DEPENDENCY INJECTION ====================

def get_execution_service(
    store: Annotated[Neo4jStore | None, Depends(get_neo4j_store)]
) -> ExecutionQueryService:
    """Dependency injection for execution query service."""
    return ExecutionQueryService(store)


# ==================== ROUTES ====================

@router.get("")
def list_executions(
    service: Annotated[ExecutionQueryService, Depends(get_execution_service)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page")
):
    """
    Fetch paginated list of quantum executions.
    Used for dashboard / recent executions view.
    """
    try:
        return service.list_executions(page=page, limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")


@router.get("/{execution_id}")
def get_execution_overview(
    execution_id: str,
    service: Annotated[ExecutionQueryService, Depends(get_execution_service)]
):
    """
    Fetch execution summary, performance stats, and graph data in one response.
    Used for execution header, metrics cards, and graph visualization.
    """
    try:
        result = service.get_execution_overview(execution_id)
        if not result:
            raise HTTPException(status_code=404, detail="Execution not found")
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")


@router.get("/{execution_id}/graph")
def get_execution_graph(
    execution_id: str,
    service: Annotated[ExecutionQueryService, Depends(get_execution_service)]
):
    """
    Fetch event dependency graph for visualization.
    Returns nodes and edges for rendering the execution graph.
    """
    try:
        return service.get_execution_graph(execution_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")
