from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Event:
    event_id: int
    event_type: str
    timestamp: int

@dataclass
class GateEvent(Event):
    gate_name: str
    qubits: List[int]

@dataclass
class MeasurementEvent(Event):
    qubits: List[int]
    classical_bits: List[int]
    outcome: Optional[str] = None
