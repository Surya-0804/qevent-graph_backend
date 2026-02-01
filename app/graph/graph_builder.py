import networkx as nx

def build_event_graph(events):
    """
    Build event graph with temporal (NEXT) and data-flow (QUBIT_DEP) edges.
    
    - NEXT: Sequential temporal order of events
    - QUBIT_DEP: Data dependency based on shared qubits between events
    """
    G = nx.DiGraph()

    # Add nodes with full event data
    for event in events:
        node_data = {
            "type": event.event_type,
            "timestamp": event.timestamp
        }
        # Add qubits if available (GateEvent, MeasurementEvent)
        if hasattr(event, "qubits"):
            node_data["qubits"] = event.qubits
        # Add gate_name if available (GateEvent)
        if hasattr(event, "gate_name"):
            node_data["gate_name"] = event.gate_name
        # Add classical bits if available (MeasurementEvent)
        if hasattr(event, "classical_bits"):
            node_data["classical_bits"] = event.classical_bits
            
        G.add_node(event.event_id, **node_data)

    # Add NEXT edges (temporal order)
    for i in range(len(events) - 1):
        G.add_edge(
            events[i].event_id,
            events[i + 1].event_id,
            relation="NEXT"
        )

    # Add QUBIT_DEP edges (data-flow based on shared qubits)
    # Track last event that touched each qubit
    qubit_last_event = {}  # qubit_index -> event_id
    
    for event in events:
        if hasattr(event, "qubits") and event.qubits:
            # Find dependencies: events that last touched any of our qubits
            dependencies = set()
            for qubit in event.qubits:
                if qubit in qubit_last_event:
                    dependencies.add((qubit_last_event[qubit], qubit))
            
            # Create QUBIT_DEP edges
            for (dep_event_id, qubit) in dependencies:
                # Avoid duplicate edges, aggregate qubits if edge exists
                if G.has_edge(dep_event_id, event.event_id):
                    existing = G.edges[dep_event_id, event.event_id]
                    if existing.get("relation") == "QUBIT_DEP":
                        existing["qubits"].append(qubit)
                        continue
                
                # Only add if it's not already a NEXT edge
                if not G.has_edge(dep_event_id, event.event_id):
                    G.add_edge(
                        dep_event_id,
                        event.event_id,
                        relation="QUBIT_DEP",
                        qubits=[qubit]
                    )
            
            # Update last event for each qubit
            for qubit in event.qubits:
                qubit_last_event[qubit] = event.event_id

    return G
