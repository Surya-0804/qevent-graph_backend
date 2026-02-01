"""
Shared dependencies for the application.
"""

import os
from dotenv import load_dotenv
from app.graph.neo4j_store import Neo4jStore

load_dotenv()

_neo4j_store = None


def get_neo4j_store() -> Neo4jStore | None:
    """Get or create Neo4j store singleton."""
    global _neo4j_store
    
    if _neo4j_store is None:
        uri = os.getenv("NEO4J_URL")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        
        if uri and password:
            _neo4j_store = Neo4jStore(uri=uri, user=user, password=password)
    
    return _neo4j_store
