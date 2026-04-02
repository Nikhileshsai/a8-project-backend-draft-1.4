from qiskit import transpile, qasm2
from qiskit_aer import AerSimulator
from qiskit.quantum_info import hellinger_fidelity
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

def run_nisq_simulation(logical_circuit):
    """Transpiles to FakeManila and runs Ideal vs Noisy simulations."""
    
    backend = FakeManilaV2()
    
    # 1. Transpile for Hardware
    physical_circuit = transpile(
        logical_circuit, 
        backend=backend, 
        optimization_level=3
    )
    
    # 2. Setup Simulators
    sim_ideal = AerSimulator()
    sim_noisy = AerSimulator.from_backend(backend)
    
    # 3. Execute
    shots = 1024
    counts_ideal = sim_ideal.run(physical_circuit, shots=shots).result().get_counts()
    counts_noisy = sim_noisy.run(physical_circuit, shots=shots).result().get_counts()
    
    # 4. Benchmarking
    h_fid = hellinger_fidelity(counts_ideal, counts_noisy)
    
    return {
        "physical_circuit": physical_circuit,
        "physical_circuit_qasm": qasm2.dumps(physical_circuit),
        "counts_ideal": counts_ideal,
        "counts_noisy": counts_noisy,
        "hellinger_fidelity": h_fid,
        "backend_name": backend.name
    }
