from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.graph.neo4j_store import Neo4jStore
from app.replay.replay_engine import ReplayEngine
from app.replay.divergence import compare_executions
from app.core.dependencies import get_neo4j_store

router = APIRouter(prefix="/api/replay", tags=["Replay"])

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
    steps_a = engine.replay_execution(exec_id_a)
    steps_b = engine.replay_execution(exec_id_b)
    
    if not steps_a:
        raise HTTPException(status_code=404, detail=f"Execution {exec_id_a} not found")
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


@router.get("/{execution_id}")
def replay_execution(
    execution_id: str,
    engine: Annotated[ReplayEngine, Depends(get_engine)]
):
    """
    Return full ordered replay sequence for an execution.
    Frontend can use this for auto-play or manual step navigation.
    """
    steps = engine.replay_execution(execution_id)
    if not steps:
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "execution_id": execution_id,
        "total_steps": len(steps),
        "steps": steps
    }


@router.get("/{execution_id}/step/{step_index}")
def replay_single_step(
    execution_id: str,
    step_index: int,
    engine: Annotated[ReplayEngine, Depends(get_engine)]
):
    """
    Get a single step from the execution replay.
    Used for step-by-step navigation (Next/Previous buttons).
    """
    steps = engine.replay_execution(execution_id)

    if not steps:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    if step_index < 0 or step_index >= len(steps):
        raise HTTPException(status_code=400, detail="Invalid step index")

    return {
        "execution_id": execution_id,
        "step_index": step_index,
        "total_steps": len(steps),
        "event": steps[step_index]
    }
