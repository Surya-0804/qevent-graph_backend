# QEvent-Graph Backend

> An Event-Graph Framework for Observability and Visual Analysis of Quantum Programs

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple.svg)](https://qiskit.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-red.svg)](https://neo4j.com)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Event Schema](#event-schema)
- [Graph Model](#graph-model)
- [Noise Models](#noise-models)
- [Usage Examples](#usage-examples)
- [Performance Metrics](#performance-metrics)

---

## Overview

QEvent-Graph is a **non-intrusive observability framework** for quantum programs. Unlike traditional quantum debugging tools that rely on state inspection (which violates quantum principles), this framework captures **observable execution events** and models them as a **directed event graph**.

### Key Principles

1. **Non-Intrusive**: Only captures classical metadata, never quantum state
2. **Graph-Based**: Models execution as directed graph with temporal and data-flow edges
3. **Replay-Enabled**: Supports step-by-step replay and multi-execution comparison
4. **Noise-Aware**: Simulates realistic quantum noise for analysis

### Research Gap Addressed

Existing quantum tools lack:
- Unified execution flow observation
- Dependency analysis between operations
- Multi-run comparison capabilities
- Structured event logging as graphs

This framework addresses these gaps by treating quantum execution logs as **structured event graphs** suitable for replay-driven visual analysis.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXECUTION FLOW                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Quantum    │───▶│   Qiskit     │───▶│  Measurement │       │
│  │   Circuit    │    │  Simulator   │    │   Results    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Observable Events Only)
┌─────────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY FLOW                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │    Event     │───▶│    Graph     │───▶│    Neo4j     │       │
│  │   Logger     │    │   Builder    │    │    Store     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │                │
│                              ┌──────────────────┘                │
│                              ▼                                   │
│                     ┌──────────────┐                            │
│                     │   Replay &   │                            │
│                     │ Visualization│                            │
│                     └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Separation of Concerns**: Execution flow remains unmodified
- **Classical Metadata Only**: No quantum state inspection
- **Respects Quantum Constraints**: Destructive measurement, no-cloning theorem

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Event Logging** | Captures gate operations, measurements, execution markers |
| **Graph Construction** | Builds directed graphs with temporal (NEXT) and data-flow (QUBIT_DEP) edges |
| **Neo4j Persistence** | Stores graphs for querying and analysis |
| **Replay Engine** | Step-by-step execution replay |
| **Divergence Detection** | Compares multiple executions |
| **Noise Simulation** | Depolarizing and thermal noise models |

### Quantum Circuits Supported

| Circuit | Description | Qubits |
|---------|-------------|--------|
| `bell` | Bell state (entanglement) | 2 |
| `ghz` | GHZ state (multi-qubit entanglement) | 3 |
| `random` | Random gates (configurable) | 2 |

### Noise Models

| Model | Description | Parameters |
|-------|-------------|------------|
| `depolarizing` | Random X/Y/Z errors | `single_gate_error`, `two_gate_error`, `measurement_error` |
| `thermal` | T1/T2 relaxation | `t1`, `t2`, `gate_time` |

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.12+ | Core implementation |
| **Web Framework** | FastAPI | REST API layer |
| **Quantum Framework** | Qiskit + Qiskit-Aer | Circuit execution & noise simulation |
| **Graph Database** | Neo4j | Event graph persistence |
| **In-Memory Graph** | NetworkX | Graph construction |
| **Environment** | python-dotenv | Configuration management |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── routes.py           # Circuit execution endpoints
│   │   ├── execution_routes.py # Execution query endpoints
│   │   └── replay_routes.py    # Replay & comparison endpoints
│   ├── core/
│   │   └── dependencies.py     # Shared dependency injection
│   ├── quantum/
│   │   ├── circuits.py         # Quantum circuit definitions
│   │   ├── runner.py           # Circuit execution with Qiskit
│   │   └── noise_models.py     # Noise model implementations
│   ├── logging/
│   │   ├── event_schema.py     # Event type definitions
│   │   └── event_extractor.py  # Event extraction from circuits
│   ├── graph/
│   │   ├── graph_builder.py    # NetworkX graph construction
│   │   └── neo4j_store.py      # Neo4j persistence layer
│   ├── replay/
│   │   ├── replay_engine.py    # Execution replay logic
│   │   └── divergence.py       # Multi-execution comparison
│   └── services/
│       ├── execution_service.py      # Execution orchestration
│       └── execution_query_service.py # Query operations
├── docs/
│   ├── README.md               # This file
│   └── API.md                  # Detailed API documentation
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── stats.json                 # Performance statistics
```

---

## Installation

### Prerequisites

- Python 3.12+
- Neo4j Database (local or cloud)
- pip or uv package manager

### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/Surya-0804/qevent-graph_backend.git
cd qevent-graph_backend

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials

# 6. Start the server
uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload
```

### Verify Installation

```bash
# Check API docs
curl http://localhost:8000/docs

# Execute a test circuit
curl -X POST http://localhost:8000/api/execute/bell
```

---

## Configuration

Create a `.env` file in the project root:

```env
# Neo4j Database Configuration
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# CORS Configuration (optional)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URL` | Neo4j connection URI | Required |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Required |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |

---

## API Reference

### Base URL

```
http://localhost:8000/api
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/execute/{circuit}` | Execute a quantum circuit |
| `POST` | `/execute/{circuit}/noisy` | Execute with noise |
| `GET` | `/executions` | List all executions |
| `GET` | `/executions/{id}` | Get execution details |
| `GET` | `/executions/{id}/graph` | Get execution graph |
| `GET` | `/replay/{id}` | Full execution replay |
| `GET` | `/replay/{id}/step/{n}` | Single step replay |
| `GET` | `/replay/compare/{a}/{b}` | Compare two executions |

---

### Circuit Execution

#### Execute Circuit (Clean)

```http
POST /api/execute/{circuit_name}
```

**Parameters:**
| Name | Type | In | Description |
|------|------|-----|-------------|
| `circuit_name` | string | path | `bell`, `ghz`, or `random` |
| `gate_count` | integer | query | Number of gates (random circuit only) |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/execute/bell"
```

**Response:**
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "circuit_name": "bell",
  "num_gates": 2,
  "num_events": 6,
  "counts": {"00": 512, "11": 512},
  "events": [...],
  "nodes": [...],
  "edges": [...],
  "is_noisy": false
}
```

---

#### Execute Circuit (With Noise)

```http
POST /api/execute/{circuit_name}/noisy
```

**Parameters:**
| Name | Type | In | Description |
|------|------|-----|-------------|
| `circuit_name` | string | path | `bell`, `ghz`, or `random` |
| `noise_type` | string | query | `depolarizing` or `thermal` |
| `noise_level` | string | query | `low`, `medium`, `high`, `very_high` |
| `gate_count` | integer | query | Number of gates (random circuit only) |

**Noise Levels:**
| Level | Error Rate | Description |
|-------|------------|-------------|
| `low` | 0.1% | Near-perfect qubits |
| `medium` | 1% | Typical current hardware |
| `high` | 5% | Noisy hardware |
| `very_high` | 10% | Very noisy conditions |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/execute/bell/noisy?noise_type=depolarizing&noise_level=high"
```

**Response:**
```json
{
  "execution_id": "...",
  "circuit_name": "bell_noisy_depolarizing_high",
  "counts": {"00": 450, "11": 480, "01": 35, "10": 59},
  "is_noisy": true,
  "noise_config": {
    "noise_type": "depolarizing",
    "noise_level": "high",
    "single_gate_error": 0.05,
    "two_gate_error": 0.1,
    "measurement_error": 0.05
  }
}
```

---

### Execution Queries

#### List Executions

```http
GET /api/executions
```

**Parameters:**
| Name | Type | In | Description |
|------|------|-----|-------------|
| `page` | integer | query | Page number (default: 1) |
| `limit` | integer | query | Items per page (default: 10, max: 50) |

**Example:**
```bash
curl "http://localhost:8000/api/executions?page=1&limit=10"
```

**Response:**
```json
{
  "page": 1,
  "limit": 10,
  "total": 25,
  "executions": [
    {
      "execution_id": "...",
      "circuit_name": "bell",
      "num_events": 6,
      "created_at": "2026-02-01T14:02:48+00:00",
      "is_noisy": false
    }
  ]
}
```

---

#### Get Execution Overview

```http
GET /api/executions/{execution_id}
```

**Response:**
```json
{
  "execution_id": "...",
  "circuit_name": "bell_noisy_depolarizing_high",
  "num_events": 6,
  "created_at": "2026-02-01T14:02:48+00:00",
  "is_noisy": true,
  "noise_config": {
    "noise_type": "depolarizing",
    "noise_level": "high",
    "single_gate_error": 0.05,
    "two_gate_error": 0.1,
    "measurement_error": 0.05
  },
  "performance_stats": {
    "event_extraction_time_ms": 0.1,
    "in_memory_graph_time_ms": 0.15,
    "neo4j_persistence_time_ms": 150.5,
    "total_observability_time_ms": 150.75
  },
  "graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

---

### Replay Operations

#### Full Execution Replay

```http
GET /api/replay/{execution_id}
```

**Response:**
```json
{
  "execution_id": "...",
  "circuit_name": "bell",
  "total_steps": 6,
  "steps": [
    {"id": 0, "type": "EXECUTION_START", "timestamp": 0},
    {"id": 1, "type": "GATE", "gate": "H", "qubits": [0], "timestamp": 1},
    {"id": 2, "type": "GATE", "gate": "CX", "qubits": [0, 1], "timestamp": 2},
    {"id": 3, "type": "MEASUREMENT", "qubits": [0], "timestamp": 3},
    {"id": 4, "type": "MEASUREMENT", "qubits": [1], "timestamp": 4},
    {"id": 5, "type": "EXECUTION_END", "timestamp": 5}
  ],
  "edges": [
    {"source": 0, "target": 1, "relation": "NEXT"},
    {"source": 1, "target": 2, "relation": "NEXT"},
    {"source": 1, "target": 3, "relation": "QUBIT_DEP", "qubits": [0]}
  ],
  "is_noisy": false,
  "noise_config": null
}
```

---

#### Single Step Replay

```http
GET /api/replay/{execution_id}/step/{step_index}
```

**Parameters:**
| Name | Type | In | Description |
|------|------|-----|-------------|
| `execution_id` | string | path | Execution UUID |
| `step_index` | integer | path | 0-based step index |

**Response:**
```json
{
  "execution_id": "...",
  "circuit_name": "bell",
  "step_index": 1,
  "total_steps": 6,
  "has_next": true,
  "has_previous": true,
  "event": {
    "id": 1,
    "type": "GATE",
    "gate": "H",
    "qubits": [0],
    "timestamp": 1
  },
  "is_noisy": false
}
```

---

#### Compare Two Executions

```http
GET /api/replay/compare/{exec_id_a}/{exec_id_b}
```

**Response:**
```json
{
  "execution_a": {
    "execution_id": "...",
    "circuit_name": "bell_noisy_thermal_low",
    "is_noisy": true,
    "noise_type": "thermal",
    "noise_level": "low",
    "total_steps": 6,
    "steps": [...]
  },
  "execution_b": {
    "execution_id": "...",
    "circuit_name": "bell",
    "is_noisy": false,
    "total_steps": 6,
    "steps": [...]
  },
  "divergence_count": 0,
  "divergence_steps": [],
  "extra_events_a": [],
  "extra_events_b": []
}
```

---

## Event Schema

### Event Types

| Type | Description | Fields |
|------|-------------|--------|
| `EXECUTION_START` | Marks execution beginning | `timestamp` |
| `GATE` | Quantum gate operation | `gate`, `qubits`, `timestamp` |
| `MEASUREMENT` | Qubit measurement | `qubits`, `classical_bits`, `timestamp` |
| `EXECUTION_END` | Marks execution completion | `timestamp` |

### Event Structure

```python
class QuantumEvent:
    event_id: int           # Unique within execution
    event_type: str         # EXECUTION_START, GATE, MEASUREMENT, EXECUTION_END
    timestamp: int          # Logical timestamp (event ordering)
    gate_name: str | None   # Gate name (H, X, CX, etc.)
    qubits: list[int]       # Affected qubits
    classical_bits: list[int] | None  # Classical bits (measurements only)
```

---

## Graph Model

### Node Properties

```cypher
(:Event {
  event_id: 0,
  type: "GATE",
  gate: "H",
  qubits: [0],
  timestamp: 1
})
```

### Edge Types

| Relation | Description | Properties |
|----------|-------------|------------|
| `NEXT` | Temporal ordering | None |
| `QUBIT_DEP` | Data-flow dependency | `qubits: [int]` |

### Example Graph (Bell Circuit)

```
[EXECUTION_START] --NEXT--> [H(q0)] --NEXT--> [CX(q0,q1)] --NEXT--> [M(q0)] --NEXT--> [M(q1)] --NEXT--> [EXECUTION_END]
                              │                    │                   │                 │
                              │                    └──QUBIT_DEP(q1)────┼────────────────►│
                              └────────────────────QUBIT_DEP(q0)───────►
```

### Neo4j Schema

```cypher
// Execution node
(:Execution {
  execution_id: "uuid",
  circuit_name: "bell",
  num_events: 6,
  is_noisy: false,
  noise_type: null,
  noise_level: null,
  created_at: datetime()
})

// Event nodes linked to execution
(:Execution)-[:HAS_EVENT]->(:Event)

// Event relationships
(:Event)-[:NEXT]->(:Event)
(:Event)-[:QUBIT_DEP {qubits: [0]}]->(:Event)
```

---

## Noise Models

### Depolarizing Noise

Models random Pauli errors (X, Y, Z) with equal probability.

```python
# Error applied after each gate with probability p
# For single-qubit gates:
E(ρ) = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)
```

**Configuration:**
```json
{
  "noise_type": "depolarizing",
  "noise_level": "medium",
  "single_gate_error": 0.01,
  "two_gate_error": 0.02,
  "measurement_error": 0.01
}
```

### Thermal Relaxation Noise

Models T1 (amplitude damping) and T2 (phase damping) relaxation.

```python
# T1: Energy relaxation (|1⟩ → |0⟩ decay)
# T2: Phase coherence loss
# Constraint: T2 ≤ 2*T1
```

**Configuration:**
```json
{
  "noise_type": "thermal",
  "noise_level": "medium",
  "single_gate_error": 0.01,
  "two_gate_error": 0.02,
  "measurement_error": 0.01,
  "t1": 50.0,
  "t2": 70.0,
  "gate_time": 0.1
}
```

### Noise Level Reference

| Level | Error Rate | T1 (μs) | T2 (μs) |
|-------|------------|---------|---------|
| `low` | 0.1% | 50 | 70 |
| `medium` | 1% | 50 | 70 |
| `high` | 5% | 50 | 70 |
| `very_high` | 10% | 50 | 70 |

---

## Usage Examples

### Execute and Analyze Bell Circuit

```bash
# 1. Execute clean circuit
CLEAN=$(curl -s -X POST "http://localhost:8000/api/execute/bell" | jq -r '.execution_id')
echo "Clean execution: $CLEAN"

# 2. Execute noisy circuit
NOISY=$(curl -s -X POST "http://localhost:8000/api/execute/bell/noisy?noise_type=depolarizing&noise_level=high" | jq -r '.execution_id')
echo "Noisy execution: $NOISY"

# 3. Compare executions
curl "http://localhost:8000/api/replay/compare/$CLEAN/$NOISY" | jq
```

### Step-by-Step Replay

```bash
EXEC_ID="your-execution-id"

# Get total steps
TOTAL=$(curl -s "http://localhost:8000/api/replay/$EXEC_ID" | jq '.total_steps')

# Iterate through steps
for i in $(seq 0 $((TOTAL-1))); do
  echo "Step $i:"
  curl -s "http://localhost:8000/api/replay/$EXEC_ID/step/$i" | jq '.event'
done
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Execute circuit
response = requests.post(f"{BASE_URL}/execute/ghz")
execution = response.json()
print(f"Execution ID: {execution['execution_id']}")
print(f"Measurement counts: {execution['counts']}")

# Replay execution
replay = requests.get(f"{BASE_URL}/replay/{execution['execution_id']}").json()
for step in replay['steps']:
    print(f"Step {step['timestamp']}: {step['type']} - {step.get('gate', 'N/A')}")
```

---

## Performance Metrics

The system tracks observability overhead:

| Metric | Description | Typical Value |
|--------|-------------|---------------|
| `event_extraction_time_ms` | Time to extract events from circuit | 0.1 - 0.5 ms |
| `in_memory_graph_time_ms` | Time to build NetworkX graph | 0.1 - 0.3 ms |
| `neo4j_persistence_time_ms` | Time to store in Neo4j | 100 - 300 ms |
| `total_observability_time_ms` | Total observability overhead | 100 - 300 ms |

### Scalability Notes

- Event extraction: O(n) where n = number of gates
- Graph construction: O(n + e) where e = number of edges
- Neo4j persistence: Depends on database configuration

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Invalid request (e.g., invalid step index) |
| `404` | Execution not found |
| `422` | Validation error |
| `503` | Database unavailable |

### Error Response Format

```json
{
  "detail": "Execution not found"
}
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### Code Style

```bash
# Format code
black app/

# Lint
ruff check app/
```

### Adding New Circuit Types

1. Define circuit in `app/quantum/circuits.py`
2. Add route in `app/api/routes.py`
3. Update this documentation

---

## Developer

**Surya Abothula** - [@Surya-0804](https://github.com/Surya-0804)
