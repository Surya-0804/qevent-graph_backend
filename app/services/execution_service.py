import os
import time
import uuid
from app.quantum.runner import run_circuit
from app.logging.event_extractor import extract_events
from app.graph.graph_builder import build_event_graph
from app.graph.neo4j_store import Neo4jStore
from dotenv import load_dotenv

# Load .env from project root (searches up the directory tree)
load_dotenv()

neo4j_uri = os.getenv("NEO4J_URL", "")
neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "")
print(neo4j_uri, neo4j_user, neo4j_password)
# Initialize Neo4j only if credentials are provided
neo4j_store = None
if neo4j_uri and neo4j_user and neo4j_password:
    neo4j_store = Neo4jStore(
        uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password
    )
    print("Neo4j connection initialized")
else:
    print("Warning: Neo4j connection details not set. Running without Neo4j integration.")


def execute_with_observability(qc, name: str):
    """
    Executes a quantum circuit and captures
    observability metrics and event graph.
    """
    counts = run_circuit(qc)
    
    execution_id = str(uuid.uuid4())

    t1 = time.perf_counter()
    events = extract_events(qc)
    t2 = time.perf_counter()

    graph = build_event_graph(events)
    t3 = time.perf_counter()

    # Calculate performance metrics
    event_time = t2 - t1
    graph_time = t3 - t2
    t4 = None
    neo4j_time = None
    total_time = None

    if neo4j_store:
        t3a = time.perf_counter()
        neo4j_store.store_event_graph(
            events=events,
            execution_id=execution_id,
            edges=list(graph.edges(data=True)),
            circuit_name=name,
            performance={
                "event_extraction_time_ms": round(event_time * 1000, 4),
                "in_memory_graph_time_ms": round(graph_time * 1000, 4),
                "neo4j_persistence_time_ms": None,  # Will set below
                "total_observability_time_ms": None  # Will set below
            }
        )
        t4 = time.perf_counter()
        neo4j_time = t4 - t3a
        total_time = t4 - t1
        # Update the node with final timings (optional, for accuracy)
        neo4j_store.driver.session().run(
            """
            MATCH (x:Execution {execution_id: $execution_id})
            SET x.neo4j_persistence_time_ms = $neo4j_persistence_time_ms,
                x.total_observability_time_ms = $total_observability_time_ms
            """,
            execution_id=execution_id,
            neo4j_persistence_time_ms=round(neo4j_time * 1000, 4) if neo4j_time else None,
            total_observability_time_ms=round(total_time * 1000, 4) if total_time else None
        )
    else:
        t4 = time.perf_counter()
        total_time = t4 - t1

    return {
        "execution_id": execution_id,
        "circuit_name": name,
        "num_gates": len(qc.data),
        "num_events": len(events),
        "event_extraction_time_ms": round((t2 - t1) * 1000, 4),
        "in_memory_graph_time_ms": round((t3 - t2) * 1000, 4),
        "neo4j_persistence_time_ms": round((t4 - t3) * 1000, 4),
        "total_observability_time_ms": round((t4 - t1) * 1000, 4),
        "counts": counts,
        "events": [e.__dict__ for e in events],
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True)),
    }
