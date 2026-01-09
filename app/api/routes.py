from fastapi import APIRouter
from app.quantum.circuits import bell_circuit, ghz_circuit, random_circuit
from app.quantum.runner import run_circuit
from app.logging.event_extractor import extract_events
from app.graph.graph_builder import build_event_graph
from fastapi import HTTPException

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "healthy"}


@router.post("/execute")
def execute():
    """
    Execute a default Bell state circuit.
    """
    qc = bell_circuit()
    counts = run_circuit(qc)
    events = extract_events(qc)
    graph = build_event_graph(events)

    return {
        "counts": counts,
        "event_count": len(events),
        "events": [e.__dict__ for e in events],
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True))
    }



@router.post("/execute/{circuit_name}")
def execute_circuit(circuit_name: str):
    """
    Execute a predefined circuit by name.
    Supported circuit names: "bell", "ghz", "random"
    """
    # Select circuit based on name
    if circuit_name == "bell":
        qc = bell_circuit()
    elif circuit_name == "ghz":
        qc = ghz_circuit()
    elif circuit_name == "random":
        qc = random_circuit()
    else:
        raise HTTPException(status_code=404, detail=f"Circuit '{circuit_name}' not found")
    
    # Execute circuit and build graph
    counts = run_circuit(qc)
    events = extract_events(qc)
    graph = build_event_graph(events)

    return {
        "circuit_name": circuit_name,
        "counts": counts,
        "event_count": len(events),
        "events": [e.__dict__ for e in events],
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True))
    }
