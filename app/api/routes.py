from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "healthy"}

from app.quantum.circuits import bell_circuit
from app.quantum.runner import run_circuit
from app.logging.event_extractor import extract_events
from app.graph.graph_builder import build_event_graph

@router.post("/execute")
def execute():
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
