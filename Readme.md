qeventgraph/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes.py
│   │   ├── quantum/
│   │   │   ├── circuits.py
│   │   │   ├── runner.py
│   │   ├── logging/
│   │   │   ├── event_schema.py
│   │   │   ├── event_extractor.py
│   │   ├── graph/
│   │   │   ├── graph_builder.py
│   │   │   ├── neo4j_store.py
│   │   ├── replay/
│   │   │   ├── replay_engine.py
│   │
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── app/          # Next.js app router
│   ├── components/
│   ├── services/
│   ├── package.json
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── performance.md
│
└── README.md


┌──────────────────────────┐
│     Next.js Frontend     │
│ ─────────────────────── │
│ • Event Timeline         │
│ • Event Graph (Cytoscape)│
│ • Replay Comparison      │
│ • Performance Charts     │
└───────────▲──────────────┘
            │ REST / JSON
┌───────────┴──────────────┐
│       FastAPI Backend     │
│ ─────────────────────── │
│ • Circuit Execution      │
│ • Event Extraction       │
│ • Graph Builder          │
│ • Replay Engine          │
└───────────▲──────────────┘
            │ Graph Ops
┌───────────┴──────────────┐
│          Neo4j            │
│ ─────────────────────── │
│ • Event Nodes             │
│ • Dependency Edges        │
│ • Traversal Queries       │
└──────────────────────────┘
