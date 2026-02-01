from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from typing import Optional, Dict


def run_circuit(qc, shots: int = 1024, noise_model: Optional[NoiseModel] = None) -> Dict[str, int]:
    """
    Run a quantum circuit on the Aer simulator.
    
    Args:
        qc: QuantumCircuit to execute
        shots: Number of measurement shots
        noise_model: Optional noise model for noisy simulation
        
    Returns:
        Dictionary of measurement counts
    """
    sim = AerSimulator(noise_model=noise_model) if noise_model else AerSimulator()
    result = sim.run(qc, shots=shots).result()
    return result.get_counts()

