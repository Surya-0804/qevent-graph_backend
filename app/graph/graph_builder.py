import networkx as nx

def build_event_graph(events):
    G = nx.DiGraph()

    for event in events:
        G.add_node(
            event.event_id,
            type=event.event_type,
            timestamp=event.timestamp
        )

    for i in range(len(events) - 1):
        G.add_edge(
            events[i].event_id,
            events[i + 1].event_id,
            relation="NEXT"
        )

    return G
