from fastapi import APIRouter, HTTPException, Depends, Query
from neo4j.exceptions import ServiceUnavailable
from typing import Annotated

from app.graph.neo4j_store import Neo4jStore
from app.replay.replay_engine import ReplayEngine
from app.replay.divergence import compare_executions
from app.core.dependencies import get_neo4j_store

router = APIRouter(prefix="/api/replay", tags=["Replay"])

# Maximum allowed step index to prevent abuse
MAX_STEP_INDEX = 10000

# ==================== DEPENDENCY INJECTION ====================

def get_engine(
    store: Annotated[Neo4jStore | None, Depends(get_neo4j_store)]
) -> ReplayEngine:
    if not store:
        raise HTTPException(status_code=503, detail="Neo4j not configured")
    return ReplayEngine(store)


# ==================== ROUTES ====================

@router.get("/compare/{exec_id_a}/{exec_id_b}")
def compare_two_executions(
    exec_id_a: str,
    exec_id_b: str,
    engine: Annotated[ReplayEngine, Depends(get_engine)]
):
    """
    Compare two execution replays and detect divergence.
    Useful for comparing Bell vs GHZ, Noise vs No-noise, etc.
    """
    try:
        # Fetch first execution
        steps_a = engine.replay_execution(exec_id_a)
        if not steps_a:
            raise HTTPException(status_code=404, detail=f"Execution {exec_id_a} not found")
        
        # Fetch second execution only if first exists
        steps_b = engine.replay_execution(exec_id_b)
        if not steps_b:
            raise HTTPException(status_code=404, detail=f"Execution {exec_id_b} not found")
        
        comparison = compare_executions(steps_a, steps_b)
        
        return {
            "execution_a": exec_id_a,
            "execution_b": exec_id_b,
            "total_steps_a": len(steps_a),
            "total_steps_b": len(steps_b),
            **comparison
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")


@router.get("/{execution_id}")
def replay_execution(
    execution_id: str,
    engine: Annotated[ReplayEngine, Depends(get_engine)]
):
    """
    Return full ordered replay sequence for an execution.
    Frontend can use this for auto-play or manual step navigation.
    """
    try:
        steps = engine.replay_execution(execution_id)
        if not steps:
            raise HTTPException(status_code=404, detail="Execution not found")

        return {
            "execution_id": execution_id,
            "total_steps": len(steps),
            "steps": steps
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")


@router.get("/{execution_id}/step/{step_index}")
def replay_single_step(
    execution_id: str,
    step_index: Annotated[int, Query(ge=0, le=MAX_STEP_INDEX, description="Step index (0-based)")],
    engine: Annotated[ReplayEngine, Depends(get_engine)]
):
    """
    Get a single step from the execution replay.
    Used for step-by-step navigation (Next/Previous buttons).
    """
    try:
        steps = engine.replay_execution(execution_id)

        if not steps:
            raise HTTPException(status_code=404, detail="Execution not found")
            
        if step_index >= len(steps):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid step index. Max index is {len(steps) - 1}"
            )

        return {
            "execution_id": execution_id,
            "step_index": step_index,
            "total_steps": len(steps),
            "has_next": step_index < len(steps) - 1,
            "has_previous": step_index > 0,
            "event": steps[step_index]
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")
