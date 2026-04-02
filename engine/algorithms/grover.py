import math
from qiskit import QuantumCircuit

def build_grover_oracle(n, marked_state):
    """Constructs the phase oracle for the marked state."""
    qc = QuantumCircuit(n)
    
    # Apply X gates to states that map to '0' in the marked string
    for qubit, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            qc.x(qubit)
            
    # Multi-controlled Z gate (simulated via H - MCX - H)
    qc.h(n - 1)
    if n == 2:
        qc.cx(0, 1)
    else:
        qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    
    # Reverse the initial X gates
    for qubit, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            qc.x(qubit)
            
    return qc

def build_grover_diffuser(n):
    """Constructs the Grover diffuser (inversion about the mean)."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.x(range(n))
    
    # Multi-controlled Z gate
    qc.h(n - 1)
    if n == 2:
        qc.cx(0, 1)
    else:
        qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    
    qc.x(range(n))
    qc.h(range(n))
    return qc

def build_grover_circuit(n, marked_state):
    """Constructs the full logical Grover's circuit."""
    qc = QuantumCircuit(n, n)
    
    # State Preparation
    qc.h(range(n))
    qc.barrier()
    
    # Calculate optimal number of Grover iterations
    optimal_iterations = math.floor(math.pi / 4 * math.sqrt(2**n))
    
    oracle = build_grover_oracle(n, marked_state)
    diffuser = build_grover_diffuser(n)
    
    for _ in range(optimal_iterations):
        qc.compose(oracle, inplace=True)
        qc.barrier()
        qc.compose(diffuser, inplace=True)
        qc.barrier()
        
    # Measurement
    qc.measure(range(n), range(n))
    return qc
