from typing import List, Dict, Generator, Optional
from app.graph.neo4j_store import Neo4jStore


class ReplayEngine:
    """
    Replay engine for quantum execution graphs.
    Replays execution as an ordered sequence of observable events.
    """

    def __init__(self, store: Neo4jStore):
        self.store = store

    def replay_execution(self, execution_id: str) -> Optional[List[Dict]]:
        """
        Return full ordered replay sequence for an execution.
        
        Returns:
            List of event nodes ordered by timestamp, or None if execution not found.
        """
        graph = self.store.get_execution_graph(execution_id)
        
        # Validate that the execution exists and has nodes
        if not graph or "nodes" not in graph or not graph["nodes"]:
            return None
            
        # Nodes already ordered by timestamp
        return graph["nodes"]

    def replay_stepwise(self, execution_id: str) -> Generator[Dict, None, None]:
        """
        Generator that yields one event at a time (step-by-step replay).
        
        Yields:
            Event nodes one at a time.
            
        Note:
            Yields nothing if execution not found.
        """
        graph = self.store.get_execution_graph(execution_id)
        nodes = graph.get("nodes") if graph else None
        
        if not nodes:
            return
            
        for node in nodes:
            yield node
