from typing import List, Dict, Generator
from app.graph.neo4j_store import Neo4jStore


class ReplayEngine:
    """
    Replay engine for quantum execution graphs.
    Replays execution as an ordered sequence of observable events.
    """

    def __init__(self, store: Neo4jStore):
        self.store = store

    def replay_execution(self, execution_id: str) -> List[Dict]:
        """
        Return full ordered replay sequence for an execution.
        """
        graph = self.store.get_execution_graph(execution_id)

        # Nodes already ordered by timestamp
        return graph["nodes"]

    def replay_stepwise(self, execution_id: str) -> Generator[Dict, None, None]:
        """
        Generator that yields one event at a time (step-by-step replay).
        """
        graph = self.store.get_execution_graph(execution_id)
        for node in graph["nodes"]:
            yield node
