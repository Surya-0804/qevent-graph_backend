from typing import List, Dict


def compare_execution_sequences(exec_a: List[Dict], exec_b: List[Dict]) -> Dict:
    """
    Compare two execution event sequences and detect divergence.
    
    Compares events by type, gate name, and qubits to identify differences
    between two execution replays.
    
    Args:
        exec_a: First execution's event list
        exec_b: Second execution's event list
        
    Returns:
        Dict containing divergence_steps, extra_events_a, extra_events_b
    """
    diffs = []

    min_len = min(len(exec_a), len(exec_b))

    for i in range(min_len):
        event_a = exec_a[i]
        event_b = exec_b[i]
        
        # Get event properties safely using .get()
        type_a = event_a.get("type")
        type_b = event_b.get("type")
        gate_a = event_a.get("gate")
        gate_b = event_b.get("gate")
        qubits_a = event_a.get("qubits")
        qubits_b = event_b.get("qubits")
        
        # Check for differences in type, gate, or qubits
        if type_a != type_b or gate_a != gate_b or qubits_a != qubits_b:
            diffs.append({
                "step": i,
                "difference": {
                    "type": type_a != type_b,
                    "gate": gate_a != gate_b,
                    "qubits": qubits_a != qubits_b
                },
                "exec_a": event_a,
                "exec_b": event_b
            })

    return {
        "divergence_count": len(diffs),
        "divergence_steps": diffs,
        "extra_events_a": exec_a[min_len:],
        "extra_events_b": exec_b[min_len:]
    }


# Keep old name for backward compatibility
compare_executions = compare_execution_sequences
