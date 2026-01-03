from qiskit_aer import AerSimulator

def run_circuit(qc, shots=1024):
    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    return result.get_counts()
