from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Neo4jStore:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._connected: Optional[bool] = None

    def close(self):
        self.driver.close()

    def is_available(self) -> bool:
        """Check if Neo4j connection is available."""
        if self._connected is not None:
            return self._connected
        try:
            self.driver.verify_connectivity()
            self._connected = True
            return True
        except (ServiceUnavailable, AuthError) as e:
            logger.warning(f"Neo4j connection unavailable: {e}")
            self._connected = False
            return False

    def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """Execute a read query and return results as list of dicts."""
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            self._connected = False
            raise

    def _execute_write(self, query: str, parameters: Dict[str, Any] = None) -> None:
        """Execute a write query."""
        try:
            with self.driver.session() as session:
                session.run(query, parameters or {})
            self._connected = True
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            self._connected = False
            raise

    # ==================== WRITE OPERATIONS ====================

    def store_event_graph(self, events, execution_id: str, edges, circuit_name: str, performance: dict) -> bool:
        """Store quantum execution event graph in Neo4j, including Execution node and performance stats."""
        try:
            with self.driver.session() as session:
                # 1. Create Execution node with performance stats
                session.run(
                    """
                    CREATE (x:Execution {
                        execution_id: $execution_id,
                        circuit_name: $circuit_name,
                        event_extraction_time_ms: $event_extraction_time_ms,
                        in_memory_graph_time_ms: $in_memory_graph_time_ms,
                        neo4j_persistence_time_ms: $neo4j_persistence_time_ms,
                        total_observability_time_ms: $total_observability_time_ms,
                        created_at: datetime()
                    })
                    """,
                    execution_id=execution_id,
                    circuit_name=circuit_name,
                    event_extraction_time_ms=performance.get("event_extraction_time_ms"),
                    in_memory_graph_time_ms=performance.get("in_memory_graph_time_ms"),
                    neo4j_persistence_time_ms=performance.get("neo4j_persistence_time_ms"),
                    total_observability_time_ms=performance.get("total_observability_time_ms")
                )

                # 2. Create Event nodes and link to Execution
                event_data = [
                    {
                        "execution_id": execution_id,
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "timestamp": event.timestamp,
                        "gate_name": getattr(event, "gate_name", None),
                        "circuit_name": circuit_name
                    }
                    for event in events
                ]

                session.run(
                    """
                    UNWIND $events AS event
                    MATCH (x:Execution {execution_id: event.execution_id})
                    CREATE (e:Event {
                        execution_id: event.execution_id,
                        event_id: event.event_id,
                        event_type: event.event_type,
                        timestamp: event.timestamp,
                        gate_name: event.gate_name,
                        circuit_name: event.circuit_name
                    })
                    CREATE (x)-[:HAS_EVENT]->(e)
                    """,
                    events=event_data
                )

                # 3. Create NEXT edges in batch
                edge_data = [
                    {
                        "execution_id": execution_id,
                        "src": src,
                        "dst": dst
                    }
                    for src, dst, _ in edges
                ]

                session.run(
                    """
                    UNWIND $edges AS edge
                    MATCH (a:Event {execution_id: edge.execution_id, event_id: edge.src}),
                          (b:Event {execution_id: edge.execution_id, event_id: edge.dst})
                    CREATE (a)-[:NEXT]->(b)
                    """,
                    edges=edge_data
                )

            self._connected = True
            return True

        except ServiceUnavailable as e:
            logger.warning(f"Neo4j service unavailable, skipping graph storage: {e}")
            self._connected = False
            return False

    # ==================== READ OPERATIONS ====================

    def get_total_executions_count(self) -> int:
        """Get total count of unique executions."""
        query = """
            MATCH (e:Event)
            WITH DISTINCT e.execution_id AS exec_id
            RETURN count(exec_id) AS total
        """
        result = self._execute_query(query)
        return result[0]["total"] if result else 0

    def get_executions_paginated(self, skip: int, limit: int) -> List[Dict]:
        """Get paginated list of executions ordered by most recent (from Execution node)."""
        query = """
            MATCH (x:Execution)
            RETURN x.execution_id AS execution_id,
                   x.circuit_name AS circuit_name,
                   x.total_observability_time_ms AS total_time,
                   x.created_at AS created_at,
                   x.event_extraction_time_ms AS event_extraction_time_ms,
                   x.in_memory_graph_time_ms AS in_memory_graph_time_ms,
                   x.neo4j_persistence_time_ms AS neo4j_persistence_time_ms
            ORDER BY created_at DESC
            SKIP $skip
            LIMIT $limit
        """
        return self._execute_query(query, {"skip": skip, "limit": limit})

    def get_execution_by_id(self, execution_id: str) -> Optional[Dict]:
        """Get execution overview by ID, including performance stats."""
        query = """
            MATCH (x:Execution {execution_id: $execution_id})
            OPTIONAL MATCH (x)-[:HAS_EVENT]->(e:Event)
            RETURN
                x.execution_id AS execution_id,
                x.circuit_name AS circuit_name,
                count(e) AS num_events,
                max(e.timestamp) AS last_timestamp,
                x.event_extraction_time_ms AS event_extraction_time_ms,
                x.in_memory_graph_time_ms AS in_memory_graph_time_ms,
                x.neo4j_persistence_time_ms AS neo4j_persistence_time_ms,
                x.total_observability_time_ms AS total_observability_time_ms,
                x.created_at AS created_at
        """
        result = self._execute_query(query, {"execution_id": execution_id})
        return result[0] if result and result[0].get("execution_id") else None

    def get_execution_graph(self, execution_id: str) -> Dict[str, List[Dict]]:
        """Get event nodes and edges for graph visualization."""
        nodes_query = """
            MATCH (e:Event {execution_id: $execution_id})
            RETURN e.event_id AS id,
                   e.event_type AS type,
                   e.gate_name AS gate,
                   e.timestamp AS timestamp
            ORDER BY e.timestamp
        """
        edges_query = """
            MATCH (a:Event {execution_id: $execution_id})-[:NEXT]->(b:Event)
            RETURN a.event_id AS source,
                   b.event_id AS target
        """
        params = {"execution_id": execution_id}
        return {
            "nodes": self._execute_query(nodes_query, params),
            "edges": self._execute_query(edges_query, params)
        }
