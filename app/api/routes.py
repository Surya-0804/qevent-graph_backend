from fastapi import APIRouter, HTTPException, Query
from typing import Optional
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


@router.post("/execute/{circuit_name}/noisy")
def execute_noisy(
    circuit_name: str,
    noise_type: str = Query("depolarizing", description="Noise type: 'depolarizing' or 'thermal'"),
    noise_level: str = Query("medium", description="Noise level: 'low', 'medium', 'high', 'very_high'"),
    gate_count: int = Query(5, description="Number of gates for random circuit")
):
    """
    Execute a quantum circuit with simulated noise.
    
    This endpoint allows you to run circuits with realistic noise models to study
    the impact of errors on quantum computation.
    
    **Noise Types:**
    - **depolarizing**: Random X, Y, Z errors with equal probability. 
      Common model for gate errors.
    - **thermal**: T1/T2 relaxation noise. Models amplitude and phase damping
      in superconducting qubits.
    
    **Noise Levels:**
    - **low**: 0.1% error rate (near-perfect qubits)
    - **medium**: 1% error rate (typical current hardware)
    - **high**: 5% error rate (noisy hardware)
    - **very_high**: 10% error rate (very noisy conditions)
    
    Args:
        circuit_name: The circuit to execute ("bell", "ghz", "random")
        noise_type: Type of noise model to apply
        noise_level: Severity of noise
        gate_count: Number of gates for random circuit
        
    Returns:
        Execution results with noise configuration included
        
    Examples:
        - POST /api/execute/bell/noisy?noise_type=depolarizing&noise_level=high
        - POST /api/execute/ghz/noisy?noise_type=thermal&noise_level=medium
    """
    # Validate noise type
    if noise_type not in ["depolarizing", "thermal"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid noise_type '{noise_type}'. Choose 'depolarizing' or 'thermal'"
        )
    
    # Validate noise level
    valid_levels = ["low", "medium", "high", "very_high"]
    if noise_level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid noise_level '{noise_level}'. Choose from {valid_levels}"
        )
    
    # Get circuit
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

    return execute_with_observability(
        qc, 
        circuit_name,
        noise_type=noise_type,
        noise_level=noise_level
    )


@router.post("/execute/compare/{circuit_name}")
def execute_and_compare(
    circuit_name: str,
    noise_type: str = Query("depolarizing", description="Noise type for noisy execution"),
    noise_level: str = Query("medium", description="Noise level for noisy execution"),
    gate_count: int = Query(5, description="Number of gates for random circuit")
):
    """
    Execute the same circuit with and without noise, returning both results for comparison.
    
    This is useful for analyzing the impact of noise on quantum circuits by directly
    comparing clean (ideal) and noisy execution results.
    
    Args:
        circuit_name: The circuit to execute ("bell", "ghz", "random")
        noise_type: Type of noise model to apply
        noise_level: Severity of noise
        gate_count: Number of gates for random circuit
        
    Returns:
        Both clean and noisy execution results with comparison metrics
    """
    # Validate inputs
    if noise_type not in ["depolarizing", "thermal"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid noise_type '{noise_type}'. Choose 'depolarizing' or 'thermal'"
        )
    
    valid_levels = ["low", "medium", "high", "very_high"]
    if noise_level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid noise_level '{noise_level}'. Choose from {valid_levels}"
        )
    
    # Get circuit
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
    
    # Execute without noise (ideal)
    clean_result = execute_with_observability(qc, circuit_name)
    
    # Execute with noise
    noisy_result = execute_with_observability(
        qc,
        circuit_name,
        noise_type=noise_type,
        noise_level=noise_level
    )
    
    # Calculate fidelity approximation based on counts
    clean_counts = clean_result["counts"]
    noisy_counts = noisy_result["counts"]
    
    # Simple fidelity metric: overlap of probability distributions
    all_outcomes = set(clean_counts.keys()) | set(noisy_counts.keys())
    total_clean = sum(clean_counts.values())
    total_noisy = sum(noisy_counts.values())
    
    fidelity = 0.0
    for outcome in all_outcomes:
        p_clean = clean_counts.get(outcome, 0) / total_clean
        p_noisy = noisy_counts.get(outcome, 0) / total_noisy
        fidelity += (p_clean * p_noisy) ** 0.5  # Bhattacharyya coefficient
    
    return {
        "circuit_name": circuit_name,
        "clean_execution": clean_result,
        "noisy_execution": noisy_result,
        "comparison": {
            "fidelity": round(fidelity, 4),
            "noise_type": noise_type,
            "noise_level": noise_level,
            "clean_execution_id": clean_result["execution_id"],
            "noisy_execution_id": noisy_result["execution_id"]
        }
    }
