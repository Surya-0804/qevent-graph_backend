from fastapi import APIRouter, HTTPException
from app.quantum.circuits import bell_circuit, ghz_circuit, random_circuit
from app.services.execution_service import execute_with_observability

router = APIRouter(prefix="/api")


@router.post("/execute")
def execute_default():
    """
    Execute the default Bell state quantum circuit.
    
    This endpoint executes a 2-qubit Bell state (entangled state) circuit and returns
    measurement results along with quantum event data and the event graph.
    
    Returns:
    
        dict: Execution results containing:
            - circuit_name: Name of the circuit executed
            - counts: Measurement results from the quantum circuit
            - event_count: Total number of quantum events
            - events: List of quantum events with details
            - nodes: Graph nodes representing quantum events
            - edges: Graph edges representing event relationships
    """
    qc = bell_circuit()
    return execute_with_observability(qc, "bell")


@router.post("/execute/{circuit_name}")
def execute_named(circuit_name: str, gate_count: int = 5):
    """
    Execute a predefined quantum circuit by name.
    
    This endpoint allows you to execute different types of quantum circuits:
    - **bell**: 2-qubit Bell state (maximally entangled state)
    - **ghz**: 3-qubit GHZ state (Greenberger-Horne-Zeilinger state)
    - **random**: 2-qubit circuit with randomly applied gates
    
    Args:
    
        circuit_name (str): The name of the quantum circuit to execute. 
                           Valid options: "bell", "ghz", "random"
        gate_count (int, optional): Number of random gates to apply when circuit_name 
                                   is "random". Only applicable for random circuits.
                                   Defaults to 5. Range: 1-20 recommended.
    
    Returns:
    
        dict: Execution results containing:
            - circuit_name: Name of the circuit executed
            - counts: Measurement results from the quantum circuit
            - event_count: Total number of quantum events
            - events: List of quantum events with details
            - nodes: Graph nodes representing quantum events
            - edges: Graph edges representing event relationships
    

    Examples:
    
        - POST /api/execute/bell
        - POST /api/execute/ghz
        - POST /api/execute/random?gate_count=10
    """
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
