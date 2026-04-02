import numpy as np
from qiskit import QuantumCircuit

def build_dj_circuit(n, oracle_type):
    """Constructs the ideal logical Deutsch-Jozsa circuit."""
    qc = QuantumCircuit(n + 1, n)
    
    # State Preparation
    qc.x(n)
    qc.h(range(n + 1))
    qc.barrier()
    
    # Oracle Application
    if oracle_type == 'constant':
        if np.random.random() > 0.5:
            qc.x(n)
    elif oracle_type == 'balanced':
        for qubit in range(n):
            qc.cx(qubit, n)
            
    qc.barrier()
    
    # Interference and Measurement
    qc.h(range(n))
    qc.measure(range(n), range(n))
    
    return qc
