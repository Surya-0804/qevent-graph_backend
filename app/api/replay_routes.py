from fastapi import APIRouter, HTTPException, Depends, Path
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
    
    Returns full steps for both executions plus divergence analysis.
    """
    try:
        # Fetch first execution with metadata
        result_a = engine.replay_with_metadata(exec_id_a)
        if not result_a or not result_a["steps"]:
            raise HTTPException(status_code=404, detail=f"Execution {exec_id_a} not found")
        
        # Fetch second execution with metadata
        result_b = engine.replay_with_metadata(exec_id_b)
        if not result_b or not result_b["steps"]:
            raise HTTPException(status_code=404, detail=f"Execution {exec_id_b} not found")
        
        steps_a = result_a["steps"]
        steps_b = result_b["steps"]
        metadata_a = result_a["metadata"] or {}
        metadata_b = result_b["metadata"] or {}
        
        comparison = compare_executions(steps_a, steps_b)
        
        return {
            "execution_a": {
                "execution_id": exec_id_a,
                "circuit_name": metadata_a.get("circuit_name"),
                "is_noisy": metadata_a.get("is_noisy", False),
                "noise_type": metadata_a.get("noise_type"),
                "noise_level": metadata_a.get("noise_level"),
                "total_steps": len(steps_a),
                "steps": steps_a
            },
            "execution_b": {
                "execution_id": exec_id_b,
                "circuit_name": metadata_b.get("circuit_name"),
                "is_noisy": metadata_b.get("is_noisy", False),
                "noise_type": metadata_b.get("noise_type"),
                "noise_level": metadata_b.get("noise_level"),
                "total_steps": len(steps_b),
                "steps": steps_b
            },
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
    Includes execution metadata with noise configuration if applicable.
    """
    try:
        result = engine.replay_with_metadata(execution_id)
        if not result:
            raise HTTPException(status_code=404, detail="Execution not found")

        metadata = result["metadata"] or {}
        
        return {
            "execution_id": execution_id,
            "circuit_name": metadata.get("circuit_name"),
            "total_steps": len(result["steps"]),
            "steps": result["steps"],
            "edges": result["edges"],
            "is_noisy": metadata.get("is_noisy", False),
            "noise_config": {
                "noise_type": metadata.get("noise_type"),
                "noise_level": metadata.get("noise_level"),
                "single_gate_error": metadata.get("single_gate_error"),
                "two_gate_error": metadata.get("two_gate_error"),
                "measurement_error": metadata.get("measurement_error")
            } if metadata.get("is_noisy") else None
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")


@router.get("/{execution_id}/step/{step_index}")
def replay_single_step(
    execution_id: str,
    step_index: Annotated[int, Path(ge=0, le=MAX_STEP_INDEX, description="Step index (0-based)")],
    engine: Annotated[ReplayEngine, Depends(get_engine)]
):
    """
    Get a single step from the execution replay.
    Used for step-by-step navigation (Next/Previous buttons).
    Includes noise info if execution was noisy.
    """
    try:
        result = engine.replay_with_metadata(execution_id)

        if not result:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        steps = result["steps"]
        metadata = result["metadata"] or {}
            
        if step_index >= len(steps):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid step index. Max index is {len(steps) - 1}"
            )

        return {
            "execution_id": execution_id,
            "circuit_name": metadata.get("circuit_name"),
            "step_index": step_index,
            "total_steps": len(steps),
            "has_next": step_index < len(steps) - 1,
            "has_previous": step_index > 0,
            "event": steps[step_index],
            "is_noisy": metadata.get("is_noisy", False),
            "noise_type": metadata.get("noise_type"),
            "noise_level": metadata.get("noise_level")
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ServiceUnavailable:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")
