# QEvent-Graph Backend

> **An Event-Graph Framework for Observability and Visual Analysis of Quantum Programs**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple.svg)](https://qiskit.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-red.svg)](https://neo4j.com)

## Quick Start

```bash
# 1. Setup environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials

# 4. Run server
uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload
```

## Documentation

| Document | Description |
|----------|-------------|
| 📖 [Full README](docs/README.md) | Complete project documentation |
| 🔌 [API Reference](docs/API.md) | Detailed API documentation |
| 📊 [Swagger UI](http://localhost:8000/docs) | Interactive API explorer |

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── api/                    # REST endpoints
│   │   ├── routes.py           # Circuit execution
│   │   ├── execution_routes.py # Query endpoints
│   │   └── replay_routes.py    # Replay & compare
│   ├── quantum/                # Quantum operations
│   │   ├── circuits.py         # Bell, GHZ, Random
│   │   ├── runner.py           # Qiskit execution
│   │   └── noise_models.py     # Noise simulation
│   ├── logging/                # Event logging
│   │   ├── event_schema.py     # Event types
│   │   └── event_extractor.py  # Event extraction
│   ├── graph/                  # Graph operations
│   │   ├── graph_builder.py    # NetworkX graphs
│   │   └── neo4j_store.py      # Neo4j persistence
│   ├── replay/                 # Replay engine
│   │   ├── replay_engine.py    # Step-by-step replay
│   │   └── divergence.py       # Execution comparison
│   ├── services/               # Business logic
│   └── core/                   # Shared dependencies
├── docs/                       # Documentation
├── requirements.txt
└── .env
```

## Key Features

| Feature | Endpoint | Description |
|---------|----------|-------------|
| Execute Circuit | `POST /api/execute/{circuit}` | Run Bell, GHZ, Random |
| Execute with Noise | `POST /api/execute/{circuit}/noisy` | Depolarizing/Thermal noise |
| List Executions | `GET /api/executions` | Paginated execution list |
| Execution Details | `GET /api/executions/{id}` | Full details + graph |
| Replay Execution | `GET /api/replay/{id}` | Ordered event sequence |
| Step-by-Step | `GET /api/replay/{id}/step/{n}` | Single step navigation |
| Compare Executions | `GET /api/replay/compare/{a}/{b}` | Divergence detection |

## Environment Variables

```env
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
ALLOWED_ORIGINS=http://localhost:3000
```

## API Examples

```bash
# Execute Bell circuit
curl -X POST http://localhost:8000/api/execute/bell

# Execute with noise
curl -X POST "http://localhost:8000/api/execute/bell/noisy?noise_type=depolarizing&noise_level=high"

# List executions
curl http://localhost:8000/api/executions

# Replay execution
curl http://localhost:8000/api/replay/{execution_id}
```

## Architecture

```
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
│ • Graph Construction     │
│ • Noise Simulation       │
└───────────▲──────────────┘
            │
┌───────────┴──────────────┐
│       Neo4j Database      │
│ ─────────────────────── │
│ • Execution Nodes        │
│ • Event Nodes            │
│ • NEXT & QUBIT_DEP Edges │
└──────────────────────────┘
```
## Developer

**Surya Abothula** - [@Surya-0804](https://github.com/Surya-0804)
