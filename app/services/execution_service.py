import os
import time
import uuid
from typing import Optional, Dict, Any
from app.quantum.runner import run_circuit
from app.quantum.noise_models import get_noise_model, NoiseConfig
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


def execute_with_observability(
    qc, 
    name: str,
    noise_type: Optional[str] = None,
    noise_level: str = "medium"
) -> Dict[str, Any]:
    """
    Executes a quantum circuit and captures
    observability metrics and event graph.
    
    Args:
        qc: QuantumCircuit to execute
        name: Circuit name for identification
        noise_type: Optional noise type ("depolarizing" or "thermal")
        noise_level: Noise level ("low", "medium", "high", "very_high")
        
    Returns:
        Execution results with metrics, events, and graph data
    """
    # Get noise model if specified
    noise_model = None
    noise_config_dict = None
    if noise_type:
        noise_model, noise_config = get_noise_model(noise_type, noise_level)
        noise_config_dict = noise_config.to_dict(noise_type=noise_type, noise_level=noise_level)
        name = f"{name}_noisy_{noise_type}_{noise_level}"
    
    counts = run_circuit(qc, noise_model=noise_model)
    
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

    # Prepare noise config for storage (already includes type and level)
    noise_config_for_storage = noise_config_dict

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
            },
            noise_config=noise_config_for_storage
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
        "noise_config": noise_config_dict,
        "is_noisy": noise_type is not None
    }
