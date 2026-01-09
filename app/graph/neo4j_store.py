from neo4j import GraphDatabase

class Neo4jStore:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def store_event_graph(self, events, execution_id, edges, circuit_name: str):
        with self.driver.session() as session:
            
            #NOTE: This is just for the first testing only remove it later surya dont forget
            #TODO: Commented this out but , look for it later
            # Clear previous graph (prototype phase only)
            # session.run("MATCH (n) DETACH DELETE n")

            # Create Event nodes in batch
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
                CREATE (e:Event {
                    execution_id: event.execution_id,
                    event_id: event.event_id,
                    event_type: event.event_type,
                    timestamp: event.timestamp,
                    gate_name: event.gate_name,
                    circuit_name: event.circuit_name
                })
                """,
                events=event_data
            )

            # Create NEXT edges in batch
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
