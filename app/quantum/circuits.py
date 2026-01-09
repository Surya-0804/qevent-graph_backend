from qiskit import QuantumCircuit
import random as rand

def bell_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def ghz_circuit():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def random_circuit(num_gates=5):
    qc = QuantumCircuit(2, 2)
    for _ in range(num_gates):
        gate = rand.choice(['h', 'x', 'y', 'z'])
        qubit = rand.randint(0, 1)
        if gate == 'h':
            qc.h(qubit)
        elif gate == 'x':
            qc.x(qubit)
        elif gate == 'y':
            qc.y(qubit)
        elif gate == 'z':
            qc.z(qubit)
    qc.measure([0, 1], [0, 1])
    return qc
