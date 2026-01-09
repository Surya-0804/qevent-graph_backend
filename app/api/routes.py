from fastapi import APIRouter, HTTPException
from app.quantum.circuits import bell_circuit, ghz_circuit, random_circuit
from app.services.execution_service import execute_with_observability

router = APIRouter(prefix="/api")


@router.post("/execute")
def execute_default():
    qc = bell_circuit()
    return execute_with_observability(qc, "bell")


@router.post("/execute/{circuit_name}")
def execute_named(circuit_name: str, gate_count: int = 5):

    if circuit_name == "bell":
        qc = bell_circuit()
    elif circuit_name == "ghz":
        qc = ghz_circuit()
    elif circuit_name == "random":
        qc = random_circuit(num_gates=gate_count)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit '{circuit_name}' not found"
        )

    return execute_with_observability(qc, circuit_name)
