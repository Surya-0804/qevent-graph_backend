import time
from app.quantum.runner import run_circuit
from app.logging.event_extractor import extract_events
from app.graph.graph_builder import build_event_graph


def execute_with_observability(qc, name: str):
    """
    Executes a quantum circuit and captures
    observability metrics and event graph.
    """
    counts = run_circuit(qc)

    t1 = time.perf_counter()
    events = extract_events(qc)
    t2 = time.perf_counter()

    graph = build_event_graph(events)
    t3 = time.perf_counter()

    return {
        "circuit_name": name,
        "num_gates": len(qc.data),
        "num_events": len(events),
        "event_extraction_time_ms": round((t2 - t1) * 1000, 4),
        "graph_build_time_ms": round((t3 - t2) * 1000, 4),
        "total_observability_time_ms": round((t3 - t1) * 1000, 4),
        "counts": counts,
        "events": [e.__dict__ for e in events],
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True)),
    }
