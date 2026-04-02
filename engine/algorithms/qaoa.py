from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

def build_qaoa_circuit(n_qubits, p_layers, edges, gamma_val, beta_val):
    """Constructs a parameterized QAOA circuit for Max-Cut and binds values."""
    gamma = Parameter('γ')
    beta = Parameter('β')
    
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # State Preparation: Equal superposition
    qc.h(range(n_qubits))
    qc.barrier()
    
    for layer in range(p_layers):
        # 1. Cost Hamiltonian (Problem-specific ZZ rotations)
        for u, v in edges:
            qc.cx(u, v)
            qc.rz(2 * gamma, v)
            qc.cx(u, v)
        qc.barrier()
        
        # 2. Mixing Hamiltonian (X rotations)
        for i in range(n_qubits):
            qc.rx(2 * beta, i)
        qc.barrier()
        
    qc.measure(range(n_qubits), range(n_qubits))
    
    # Bind parameters for the specific snapshot
    bound_qc = qc.assign_parameters({
        gamma: gamma_val, 
        beta: beta_val
    })
    
    return bound_qc
