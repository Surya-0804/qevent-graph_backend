"""
Service layer for execution query operations.
Handles business logic for retrieving execution data from Neo4j.
"""

from typing import Optional, Dict, List, Any
from app.graph.neo4j_store import Neo4jStore


class ExecutionQueryService:
    """Service for querying quantum execution data."""

    def __init__(self, neo4j_store: Optional[Neo4jStore]):
        self._store = neo4j_store

    @property
    def is_available(self) -> bool:
        """Check if the service is available."""
        return self._store is not None and self._store.is_available()

    def list_executions(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Get paginated list of quantum executions from Neo4j Execution node.
        """
        if not self._store:
            raise RuntimeError("Neo4j not configured")

        skip = (page - 1) * limit
        total = self._store.get_total_executions_count()
        executions = self._store.get_executions_paginated(skip, limit)

        enriched = []
        for e in executions:
            # Format created_at datetime properly
            created_at = e.get("created_at")
            if created_at and hasattr(created_at, 'isoformat'):
                created_at = created_at.isoformat()

            item = {
                "execution_id": e.get("execution_id"),
                "circuit_name": e.get("circuit_name"),
                "num_events": e.get("num_events"),
                "event_count": e.get("num_events"),
                "time": e.get("total_time"),
                "created_at": created_at,
                "is_noisy": e.get("is_noisy", False),
            }

            # Group noise config if execution is noisy
            if e.get("is_noisy"):
                item["noise_config"] = {
                    "noise_type": e.get("noise_type"),
                    "noise_level": e.get("noise_level"),
                }

            enriched.append(item)

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "executions": enriched
        }

    def get_execution_overview(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution summary, performance stats, and graph data from Neo4j.
        """
        if not self._store:
            raise RuntimeError("Neo4j not configured")

        # Basic info and stats from Neo4j
        basic = self._store.get_execution_by_id(execution_id)
        if not basic:
            return None

        # Graph data from Neo4j
        graph = self._store.get_execution_graph(execution_id)

        # Format created_at datetime properly
        created_at = basic.get("created_at")
        if created_at and hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()

        # Build clean response with grouped noise_config
        overview = {
            "execution_id": basic.get("execution_id"),
            "circuit_name": basic.get("circuit_name"),
            "num_events": basic.get("num_events"),
            "last_timestamp": basic.get("last_timestamp"),
            "created_at": created_at,
            "is_noisy": basic.get("is_noisy", False),
        }

        # Group noise config if execution is noisy
        if basic.get("is_noisy"):
            overview["noise_config"] = {
                "noise_type": basic.get("noise_type"),
                "noise_level": basic.get("noise_level"),
                "single_gate_error": basic.get("single_gate_error"),
                "two_gate_error": basic.get("two_gate_error"),
                "measurement_error": basic.get("measurement_error"),
            }

        # Performance stats
        overview["performance_stats"] = {
            "event_extraction_time_ms": basic.get("event_extraction_time_ms"),
            "in_memory_graph_time_ms": basic.get("in_memory_graph_time_ms"),
            "neo4j_persistence_time_ms": basic.get("neo4j_persistence_time_ms"),
            "total_observability_time_ms": basic.get("total_observability_time_ms"),
        }

        overview["graph"] = graph
        return overview

    def get_execution_graph(self, execution_id: str) -> Dict[str, List[Dict]]:
        """
        Get event dependency graph for visualization.
        
        Args:
            execution_id: UUID of the execution
            
        Returns:
            Dict with nodes and edges lists
            
        Raises:
            RuntimeError: If Neo4j is not configured
        """
        if not self._store:
            raise RuntimeError("Neo4j not configured")

        return self._store.get_execution_graph(execution_id)
