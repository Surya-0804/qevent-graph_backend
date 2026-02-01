"""
Noise models for quantum circuit simulation.
Provides configurable noise models using Qiskit Aer.
"""

from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error
from typing import Optional, Dict, Any


class NoiseConfig:
    """Configuration for quantum noise simulation."""
    
    # Predefined noise levels
    NOISE_LEVELS = {
        "low": 0.001,      # 0.1% error rate
        "medium": 0.01,    # 1% error rate  
        "high": 0.05,      # 5% error rate
        "very_high": 0.1   # 10% error rate
    }
    
    def __init__(
        self,
        single_gate_error: float = 0.01,
        two_gate_error: float = 0.02,
        measurement_error: float = 0.01,
        t1: Optional[float] = None,  # T1 relaxation time (microseconds)
        t2: Optional[float] = None,  # T2 dephasing time (microseconds)
        gate_time: float = 0.1       # Gate time (microseconds)
    ):
        self.single_gate_error = single_gate_error
        self.two_gate_error = two_gate_error
        self.measurement_error = measurement_error
        self.t1 = t1
        self.t2 = t2
        self.gate_time = gate_time
    
    @classmethod
    def from_level(cls, level: str) -> "NoiseConfig":
        """Create noise config from predefined level."""
        if level not in cls.NOISE_LEVELS:
            raise ValueError(f"Unknown noise level: {level}. Choose from {list(cls.NOISE_LEVELS.keys())}")
        
        error_rate = cls.NOISE_LEVELS[level]
        return cls(
            single_gate_error=error_rate,
            two_gate_error=error_rate * 2,
            measurement_error=error_rate
        )
    
    def to_dict(self, noise_type: str = None, noise_level: str = None) -> Dict[str, Any]:
        """Convert config to dictionary for API response.
        
        Only includes relevant fields based on noise type:
        - depolarizing: error rates only
        - thermal: T1/T2 and gate time
        """
        result = {
            "noise_type": noise_type,
            "noise_level": noise_level,
            "single_gate_error": self.single_gate_error,
            "two_gate_error": self.two_gate_error,
            "measurement_error": self.measurement_error,
        }
        
        # Only include T1/T2 for thermal noise
        if noise_type == "thermal":
            result["t1"] = self.t1
            result["t2"] = self.t2
            result["gate_time"] = self.gate_time
        
        return result


def create_depolarizing_noise_model(config: NoiseConfig) -> NoiseModel:
    """
    Create a depolarizing noise model.
    
    Depolarizing noise randomly applies X, Y, or Z errors with equal probability.
    This is a common model for gate errors in quantum computers.
    """
    noise_model = NoiseModel()
    
    # Single-qubit gate errors
    single_gate_error = depolarizing_error(config.single_gate_error, 1)
    noise_model.add_all_qubit_quantum_error(single_gate_error, ['h', 'x', 'y', 'z', 's', 't'])
    
    # Two-qubit gate errors (CX, CZ, etc.)
    two_gate_error = depolarizing_error(config.two_gate_error, 2)
    noise_model.add_all_qubit_quantum_error(two_gate_error, ['cx', 'cz', 'swap'])
    
    # Measurement errors (readout errors)
    if config.measurement_error > 0:
        meas_error = depolarizing_error(config.measurement_error, 1)
        noise_model.add_all_qubit_quantum_error(meas_error, ['measure'])
    
    return noise_model


def create_thermal_noise_model(config: NoiseConfig) -> NoiseModel:
    """
    Create a thermal relaxation noise model.
    
    Models T1 (amplitude damping) and T2 (phase damping) relaxation,
    which are the dominant noise sources in superconducting qubits.
    """
    if config.t1 is None or config.t2 is None:
        raise ValueError("T1 and T2 must be specified for thermal noise model")
    
    noise_model = NoiseModel()
    
    # Thermal relaxation error for single-qubit gates
    thermal_error_1q = thermal_relaxation_error(
        config.t1, 
        config.t2, 
        config.gate_time
    )
    noise_model.add_all_qubit_quantum_error(thermal_error_1q, ['h', 'x', 'y', 'z', 's', 't'])
    
    # Thermal relaxation error for two-qubit gates (longer gate time)
    thermal_error_2q = thermal_relaxation_error(
        config.t1,
        config.t2,
        config.gate_time * 2  # Two-qubit gates typically take longer
    ).tensor(thermal_relaxation_error(
        config.t1,
        config.t2,
        config.gate_time * 2
    ))
    noise_model.add_all_qubit_quantum_error(thermal_error_2q, ['cx', 'cz'])
    
    return noise_model


def get_noise_model(
    noise_type: str = "depolarizing",
    level: str = "medium",
    custom_config: Optional[NoiseConfig] = None
) -> tuple[NoiseModel, NoiseConfig]:
    """
    Get a noise model by type and level.
    
    Args:
        noise_type: Type of noise ("depolarizing" or "thermal")
        level: Noise level ("low", "medium", "high", "very_high")
        custom_config: Optional custom noise configuration
        
    Returns:
        Tuple of (NoiseModel, NoiseConfig)
    """
    config = custom_config or NoiseConfig.from_level(level)
    
    if noise_type == "depolarizing":
        return create_depolarizing_noise_model(config), config
    elif noise_type == "thermal":
        if config.t1 is None:
            # Default T1/T2 values for superconducting qubits
            config.t1 = 50.0  # 50 microseconds
            config.t2 = 70.0  # 70 microseconds
        return create_thermal_noise_model(config), config
    else:
        raise ValueError(f"Unknown noise type: {noise_type}. Choose 'depolarizing' or 'thermal'")
