from typing import List, Dict

def compare_executions(exec_a: List[Dict], exec_b: List[Dict]) -> Dict:
    """
    Compare two execution replays and detect divergence.
    """
    diffs = []

    min_len = min(len(exec_a), len(exec_b))

    for i in range(min_len):
        if exec_a[i]["type"] != exec_b[i]["type"]:
            diffs.append({
                "step": i,
                "exec_a": exec_a[i],
                "exec_b": exec_b[i]
            })

    return {
        "divergence_steps": diffs,
        "extra_events_a": exec_a[min_len:],
        "extra_events_b": exec_b[min_len:]
    }
