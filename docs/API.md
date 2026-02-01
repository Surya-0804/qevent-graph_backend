# QEvent-Graph API Documentation

> Complete API Reference for the Quantum Event Graph Backend

## Base Configuration

| Property | Value |
|----------|-------|
| Base URL | `http://localhost:8000` |
| API Prefix | `/api` |
| Content-Type | `application/json` |
| Documentation | `/docs` (Swagger UI) |
| Alternative Docs | `/redoc` (ReDoc) |

---

## Authentication

Currently, no authentication is required. For production deployment, consider adding:
- API Key authentication
- JWT tokens
- OAuth2

---

## Rate Limiting

No rate limiting is implemented. For production, consider:
- Request throttling per IP
- Circuit execution limits

---

## Endpoints

### 1. Circuit Execution (`/api/execute`)

#### 1.1 Execute Clean Circuit

Executes a quantum circuit without noise simulation.

```http
POST /api/execute/{circuit_name}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `circuit_name` | string | Yes | One of: `bell`, `ghz`, `random` |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gate_count` | integer | No | 5 | Number of gates (only for `random` circuit) |

**Request Example:**

```bash
# Bell circuit
curl -X POST "http://localhost:8000/api/execute/bell"

# GHZ circuit
curl -X POST "http://localhost:8000/api/execute/ghz"

# Random circuit with 10 gates
curl -X POST "http://localhost:8000/api/execute/random?gate_count=10"
```

**Response Schema:**

```typescript
interface ExecutionResponse {
  execution_id: string;          // UUID
  circuit_name: string;          // e.g., "bell"
  num_gates: number;             // Number of quantum gates
  num_events: number;            // Total events logged
  event_extraction_time_ms: number;
  in_memory_graph_time_ms: number;
  neo4j_persistence_time_ms: number;
  total_observability_time_ms: number;
  counts: Record<string, number>; // Measurement results
  events: Event[];               // List of events
  nodes: [number, NodeData][];   // Graph nodes
  edges: [number, number, EdgeData][]; // Graph edges
  noise_config: null;            // null for clean execution
  is_noisy: false;
}
```

**Response Example:**

```json
{
  "execution_id": "f5e631d4-6447-4ffe-8f13-16989d9541ee",
  "circuit_name": "bell",
  "num_gates": 2,
  "num_events": 6,
  "event_extraction_time_ms": 0.0892,
  "in_memory_graph_time_ms": 0.1023,
  "neo4j_persistence_time_ms": 145.2341,
  "total_observability_time_ms": 145.4256,
  "counts": {
    "00": 498,
    "11": 526
  },
  "events": [
    {
      "event_id": 0,
      "event_type": "EXECUTION_START",
      "timestamp": 0
    },
    {
      "event_id": 1,
      "event_type": "GATE",
      "timestamp": 1,
      "gate_name": "H",
      "qubits": [0]
    },
    {
      "event_id": 2,
      "event_type": "GATE",
      "timestamp": 2,
      "gate_name": "CX",
      "qubits": [0, 1]
    },
    {
      "event_id": 3,
      "event_type": "MEASUREMENT",
      "timestamp": 3,
      "qubits": [0],
      "classical_bits": [0],
      "outcome": null
    },
    {
      "event_id": 4,
      "event_type": "MEASUREMENT",
      "timestamp": 4,
      "qubits": [1],
      "classical_bits": [1],
      "outcome": null
    },
    {
      "event_id": 5,
      "event_type": "EXECUTION_END",
      "timestamp": 5
    }
  ],
  "nodes": [
    [0, {"type": "EXECUTION_START", "timestamp": 0}],
    [1, {"type": "GATE", "timestamp": 1, "qubits": [0], "gate_name": "H"}],
    [2, {"type": "GATE", "timestamp": 2, "qubits": [0, 1], "gate_name": "CX"}],
    [3, {"type": "MEASUREMENT", "timestamp": 3, "qubits": [0], "classical_bits": [0]}],
    [4, {"type": "MEASUREMENT", "timestamp": 4, "qubits": [1], "classical_bits": [1]}],
    [5, {"type": "EXECUTION_END", "timestamp": 5}]
  ],
  "edges": [
    [0, 1, {"relation": "NEXT"}],
    [1, 2, {"relation": "NEXT"}],
    [1, 3, {"relation": "QUBIT_DEP", "qubits": [0]}],
    [2, 3, {"relation": "NEXT"}],
    [2, 4, {"relation": "QUBIT_DEP", "qubits": [1]}],
    [3, 4, {"relation": "NEXT"}],
    [4, 5, {"relation": "NEXT"}]
  ],
  "noise_config": null,
  "is_noisy": false
}
```

---

#### 1.2 Execute Noisy Circuit

Executes a quantum circuit with simulated noise.

```http
POST /api/execute/{circuit_name}/noisy
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `circuit_name` | string | Yes | One of: `bell`, `ghz`, `random` |

**Query Parameters:**

| Parameter | Type | Required | Default | Options | Description |
|-----------|------|----------|---------|---------|-------------|
| `noise_type` | string | No | `depolarizing` | `depolarizing`, `thermal` | Type of noise model |
| `noise_level` | string | No | `medium` | `low`, `medium`, `high`, `very_high` | Severity of noise |
| `gate_count` | integer | No | 5 | 1-100 | Gates for random circuit |

**Noise Level Reference:**

| Level | Error Rate | Use Case |
|-------|------------|----------|
| `low` | 0.1% (0.001) | Near-perfect qubits |
| `medium` | 1% (0.01) | Typical current hardware |
| `high` | 5% (0.05) | Noisy hardware |
| `very_high` | 10% (0.1) | Very noisy conditions |

**Request Examples:**

```bash
# Depolarizing noise (high)
curl -X POST "http://localhost:8000/api/execute/bell/noisy?noise_type=depolarizing&noise_level=high"

# Thermal noise (medium)
curl -X POST "http://localhost:8000/api/execute/ghz/noisy?noise_type=thermal&noise_level=medium"

# Random circuit with noise
curl -X POST "http://localhost:8000/api/execute/random/noisy?noise_type=depolarizing&noise_level=low&gate_count=8"
```

**Response Schema (Noisy):**

```typescript
interface NoisyExecutionResponse extends ExecutionResponse {
  is_noisy: true;
  noise_config: {
    noise_type: "depolarizing" | "thermal";
    noise_level: "low" | "medium" | "high" | "very_high";
    single_gate_error: number;
    two_gate_error: number;
    measurement_error: number;
    // Only for thermal noise:
    t1?: number;          // T1 relaxation time (μs)
    t2?: number;          // T2 dephasing time (μs)
    gate_time?: number;   // Gate operation time (μs)
  };
}
```

**Response Example (Depolarizing):**

```json
{
  "execution_id": "77ed73fb-66c8-415a-9c82-d576aa887f1e",
  "circuit_name": "bell_noisy_depolarizing_high",
  "num_gates": 2,
  "num_events": 6,
  "counts": {
    "00": 450,
    "11": 480,
    "01": 35,
    "10": 59
  },
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

**Response Example (Thermal):**

```json
{
  "execution_id": "18f66671-dbf7-41ba-bdea-1ed6c36c1e31",
  "circuit_name": "bell_noisy_thermal_medium",
  "is_noisy": true,
  "noise_config": {
    "noise_type": "thermal",
    "noise_level": "medium",
    "single_gate_error": 0.01,
    "two_gate_error": 0.02,
    "measurement_error": 0.01,
    "t1": 50.0,
    "t2": 70.0,
    "gate_time": 0.1
  }
}
```

---

### 2. Execution Queries (`/api/executions`)

#### 2.1 List Executions

Retrieve paginated list of all executions.

```http
GET /api/executions
```

**Query Parameters:**

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `page` | integer | No | 1 | ≥1 | Page number |
| `limit` | integer | No | 10 | 1-50 | Items per page |

**Request Examples:**

```bash
# Default (page 1, 10 items)
curl "http://localhost:8000/api/executions"

# Custom pagination
curl "http://localhost:8000/api/executions?page=2&limit=20"
```

**Response Schema:**

```typescript
interface ExecutionListResponse {
  page: number;
  limit: number;
  total: number;
  executions: ExecutionSummary[];
}

interface ExecutionSummary {
  execution_id: string;
  circuit_name: string;
  num_events: number;
  event_count: number;       // Alias for num_events
  time: number | null;       // Total execution time
  created_at: string;        // ISO 8601 datetime
  is_noisy: boolean;
  noise_config?: {           // Only if is_noisy=true
    noise_type: string;
    noise_level: string;
  };
}
```

**Response Example:**

```json
{
  "page": 1,
  "limit": 10,
  "total": 25,
  "executions": [
    {
      "execution_id": "0591bf1a-7889-478c-8596-3bf57ff974be",
      "circuit_name": "ghz_noisy_depolarizing_very_high",
      "num_events": 8,
      "event_count": 8,
      "time": 165.234,
      "created_at": "2026-02-01T14:30:00+00:00",
      "is_noisy": true,
      "noise_config": {
        "noise_type": "depolarizing",
        "noise_level": "very_high"
      }
    },
    {
      "execution_id": "f5e631d4-6447-4ffe-8f13-16989d9541ee",
      "circuit_name": "bell",
      "num_events": 6,
      "event_count": 6,
      "time": 145.425,
      "created_at": "2026-02-01T14:25:00+00:00",
      "is_noisy": false
    }
  ]
}
```

---

#### 2.2 Get Execution Overview

Retrieve detailed execution information with graph data.

```http
GET /api/executions/{execution_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `execution_id` | string | Yes | UUID of the execution |

**Request Example:**

```bash
curl "http://localhost:8000/api/executions/f5e631d4-6447-4ffe-8f13-16989d9541ee"
```

**Response Schema:**

```typescript
interface ExecutionOverviewResponse {
  execution_id: string;
  circuit_name: string;
  num_events: number;
  last_timestamp: number;
  created_at: string;          // ISO 8601 datetime
  is_noisy: boolean;
  noise_config?: NoiseConfig;  // Only if is_noisy=true
  performance_stats: {
    event_extraction_time_ms: number;
    in_memory_graph_time_ms: number;
    neo4j_persistence_time_ms: number;
    total_observability_time_ms: number;
  };
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
}

interface GraphNode {
  id: number;
  type: string;
  gate: string | null;
  qubits: number[] | null;
  timestamp: number;
}

interface GraphEdge {
  source: number;
  target: number;
  relation: "NEXT" | "QUBIT_DEP";
  qubits?: number[];  // Only for QUBIT_DEP
}
```

**Response Example:**

```json
{
  "execution_id": "bbe59136-254e-428a-b035-3c24a09065fe",
  "circuit_name": "random_noisy_depolarizing_medium",
  "num_events": 9,
  "last_timestamp": 8,
  "created_at": "2026-02-01T14:02:48+00:00",
  "is_noisy": true,
  "noise_config": {
    "noise_type": "depolarizing",
    "noise_level": "medium",
    "single_gate_error": 0.01,
    "two_gate_error": 0.02,
    "measurement_error": 0.01
  },
  "performance_stats": {
    "event_extraction_time_ms": 0.0968,
    "in_memory_graph_time_ms": 0.1106,
    "neo4j_persistence_time_ms": 159.1835,
    "total_observability_time_ms": 159.3942
  },
  "graph": {
    "nodes": [
      {"id": 0, "type": "EXECUTION_START", "gate": null, "qubits": null, "timestamp": 0},
      {"id": 1, "type": "GATE", "gate": "H", "qubits": [0], "timestamp": 1},
      {"id": 2, "type": "GATE", "gate": "CX", "qubits": [0, 1], "timestamp": 2}
    ],
    "edges": [
      {"source": 0, "target": 1, "relation": "NEXT"},
      {"source": 1, "target": 2, "relation": "NEXT"},
      {"source": 1, "target": 3, "relation": "QUBIT_DEP", "qubits": [0]}
    ]
  }
}
```

---

#### 2.3 Get Execution Graph

Retrieve only the graph data for an execution.

```http
GET /api/executions/{execution_id}/graph
```

**Request Example:**

```bash
curl "http://localhost:8000/api/executions/f5e631d4-6447-4ffe-8f13-16989d9541ee/graph"
```

**Response Schema:**

```typescript
interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
```

---

### 3. Replay Operations (`/api/replay`)

#### 3.1 Full Execution Replay

Retrieve complete ordered sequence for replay.

```http
GET /api/replay/{execution_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `execution_id` | string | Yes | UUID of the execution |

**Request Example:**

```bash
curl "http://localhost:8000/api/replay/f5e631d4-6447-4ffe-8f13-16989d9541ee"
```

**Response Schema:**

```typescript
interface ReplayResponse {
  execution_id: string;
  circuit_name: string;
  total_steps: number;
  steps: ReplayStep[];
  edges: GraphEdge[];
  is_noisy: boolean;
  noise_config: NoiseConfig | null;
}

interface ReplayStep {
  id: number;
  type: string;
  gate: string | null;
  qubits: number[] | null;
  timestamp: number;
}
```

**Response Example:**

```json
{
  "execution_id": "f5e631d4-6447-4ffe-8f13-16989d9541ee",
  "circuit_name": "bell",
  "total_steps": 6,
  "steps": [
    {"id": 0, "type": "EXECUTION_START", "gate": null, "qubits": null, "timestamp": 0},
    {"id": 1, "type": "GATE", "gate": "H", "qubits": [0], "timestamp": 1},
    {"id": 2, "type": "GATE", "gate": "CX", "qubits": [0, 1], "timestamp": 2},
    {"id": 3, "type": "MEASUREMENT", "gate": null, "qubits": [0], "timestamp": 3},
    {"id": 4, "type": "MEASUREMENT", "gate": null, "qubits": [1], "timestamp": 4},
    {"id": 5, "type": "EXECUTION_END", "gate": null, "qubits": null, "timestamp": 5}
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

#### 3.2 Single Step Replay

Retrieve a specific step from execution replay.

```http
GET /api/replay/{execution_id}/step/{step_index}
```

**Path Parameters:**

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `execution_id` | string | Yes | UUID | Execution identifier |
| `step_index` | integer | Yes | 0 ≤ n ≤ 10000 | 0-based step index |

**Request Example:**

```bash
# Get step 2
curl "http://localhost:8000/api/replay/f5e631d4-6447-4ffe-8f13-16989d9541ee/step/2"
```

**Response Schema:**

```typescript
interface SingleStepResponse {
  execution_id: string;
  circuit_name: string;
  step_index: number;
  total_steps: number;
  has_next: boolean;
  has_previous: boolean;
  event: ReplayStep;
  is_noisy: boolean;
  noise_type: string | null;
  noise_level: string | null;
}
```

**Response Example:**

```json
{
  "execution_id": "f5e631d4-6447-4ffe-8f13-16989d9541ee",
  "circuit_name": "bell",
  "step_index": 2,
  "total_steps": 6,
  "has_next": true,
  "has_previous": true,
  "event": {
    "id": 2,
    "type": "GATE",
    "gate": "CX",
    "qubits": [0, 1],
    "timestamp": 2
  },
  "is_noisy": false,
  "noise_type": null,
  "noise_level": null
}
```

---

#### 3.3 Compare Two Executions

Compare two execution replays and detect divergence.

```http
GET /api/replay/compare/{exec_id_a}/{exec_id_b}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exec_id_a` | string | Yes | UUID of first execution |
| `exec_id_b` | string | Yes | UUID of second execution |

**Request Example:**

```bash
curl "http://localhost:8000/api/replay/compare/e4895724-4178-48d6-91a5-8815b001c1d6/f5e631d4-6447-4ffe-8f13-16989d9541ee"
```

**Response Schema:**

```typescript
interface CompareResponse {
  execution_a: ExecutionDetail;
  execution_b: ExecutionDetail;
  divergence_count: number;
  divergence_steps: DivergenceStep[];
  extra_events_a: ReplayStep[];
  extra_events_b: ReplayStep[];
}

interface ExecutionDetail {
  execution_id: string;
  circuit_name: string;
  is_noisy: boolean;
  noise_type: string | null;
  noise_level: string | null;
  total_steps: number;
  steps: ReplayStep[];
}

interface DivergenceStep {
  step: number;
  difference: {
    type: boolean;    // true if types differ
    gate: boolean;    // true if gates differ
    qubits: boolean;  // true if qubits differ
  };
  exec_a: ReplayStep;
  exec_b: ReplayStep;
}
```

**Response Example:**

```json
{
  "execution_a": {
    "execution_id": "e4895724-4178-48d6-91a5-8815b001c1d6",
    "circuit_name": "bell_noisy_thermal_low",
    "is_noisy": true,
    "noise_type": "thermal",
    "noise_level": "low",
    "total_steps": 6,
    "steps": [
      {"id": 0, "type": "EXECUTION_START", "gate": null, "qubits": null, "timestamp": 0},
      {"id": 1, "type": "GATE", "gate": "H", "qubits": [0], "timestamp": 1}
    ]
  },
  "execution_b": {
    "execution_id": "f5e631d4-6447-4ffe-8f13-16989d9541ee",
    "circuit_name": "bell",
    "is_noisy": false,
    "noise_type": null,
    "noise_level": null,
    "total_steps": 6,
    "steps": [
      {"id": 0, "type": "EXECUTION_START", "gate": null, "qubits": null, "timestamp": 0},
      {"id": 1, "type": "GATE", "gate": "H", "qubits": [0], "timestamp": 1}
    ]
  },
  "divergence_count": 0,
  "divergence_steps": [],
  "extra_events_a": [],
  "extra_events_b": []
}
```

**Divergence Detection Logic:**

The comparison checks each step for differences in:
- Event type (GATE, MEASUREMENT, etc.)
- Gate name (H, CX, X, Y, Z, etc.)
- Affected qubits

> **Note:** Noise doesn't change the event structure—it only affects measurement outcomes (the `counts` field). Two executions of the same circuit (one clean, one noisy) will have `divergence_count: 0`.

---

## Error Responses

### Error Schema

```typescript
interface ErrorResponse {
  detail: string | ValidationError[];
}

interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
```

### HTTP Status Codes

| Code | Description | Example Cause |
|------|-------------|---------------|
| `200` | Success | Request completed |
| `400` | Bad Request | Invalid step index |
| `404` | Not Found | Execution doesn't exist |
| `422` | Validation Error | Invalid query parameters |
| `503` | Service Unavailable | Neo4j connection failed |

### Error Examples

**404 Not Found:**
```json
{
  "detail": "Execution not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Invalid step index. Max index is 5"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["query", "noise_type"],
      "msg": "value is not a valid enumeration member; permitted: 'depolarizing', 'thermal'",
      "type": "type_error.enum"
    }
  ]
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Neo4j not configured"
}
```

---

## WebSocket Support (Future)

> Currently not implemented. Planned for future releases.

Potential endpoints:
- `/ws/replay/{execution_id}` - Real-time step streaming
- `/ws/execute` - Live execution with event streaming

---

## Changelog

### v1.0.0 (Review 3)

- ✅ Core circuit execution (Bell, GHZ, Random)
- ✅ Event logging and graph construction
- ✅ Neo4j persistence
- ✅ Noise models (Depolarizing, Thermal)
- ✅ Replay engine with step-by-step navigation
- ✅ Execution comparison and divergence detection
- ✅ QUBIT_DEP edges for data-flow analysis
