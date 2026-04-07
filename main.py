from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from fractions import Fraction
import numpy as np
from qiskit import qasm2

# Engine Imports
from engine.algorithms.deutsch_jozsa import build_dj_circuit
from engine.algorithms.grover import build_grover_circuit
from engine.algorithms.qaoa import build_qaoa_circuit
from engine.visualization.zx_processor import generate_zx_graphs
from engine.visualization.circuit_renderer import circuit_to_svg
from engine.simulators.qiskit_sim import run_nisq_simulation

app = FastAPI(title="NISQ Visualizer API")

@app.get("/")
async def root():
    return {"status": "alive", "message": "NISQ Visualizer Backend is running"}

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DJParams(BaseModel):
    n_qubits: int
    oracle_type: str
    target_noisy_qubit: int = 0
    phase_drift: float = 0.25
    backend_name: str = "FakeManilaV2"

class GroverParams(BaseModel):
    n_qubits: int
    marked_state: str
    target_noisy_qubit: int = 0
    phase_drift: float = 0.25
    backend_name: str = "FakeManilaV2"

class QAOAParams(BaseModel):
    n_qubits: int
    p_layers: int
    edges: List[List[int]]
    gamma: float = np.pi / 3
    beta: float = np.pi / 4
    target_noisy_qubit: int = 0
    phase_drift: float = 0.25
    backend_name: str = "FakeManilaV2"

class CustomParams(BaseModel):
    qasm: str
    target_noisy_qubit: int = 0
    phase_drift: float = 0.25
    backend_name: str = "FakeManilaV2"

def pad_counts(counts: Dict[str, int], n_qubits: int) -> Dict[str, int]:
    """Pads counts with 0 for all 2^n possible states."""
    all_states = [bin(i)[2:].zfill(n_qubits) for i in range(2**n_qubits)]
    return {state: counts.get(state, 0) for state in all_states}

def format_backend_name(name: str) -> str:
    """Formats backend name for display (e.g., fake_manila -> Manila)."""
    return name.replace("fake_", "").capitalize()

@app.post("/algorithms/deutsch-jozsa")
async def execute_dj(params: DJParams):
    logical_qc = build_dj_circuit(params.n_qubits, params.oracle_type)
    sim_data = run_nisq_simulation(logical_qc, params.backend_name)
    zx_data = generate_zx_graphs(
        sim_data["physical_circuit"], 
        params.target_noisy_qubit, 
        Fraction(params.phase_drift).limit_denominator()
    )
    
    # Pad counts for the full noise floor view
    counts_ideal = pad_counts(sim_data["counts_ideal"], params.n_qubits)
    counts_noisy = pad_counts(sim_data["counts_noisy"], params.n_qubits)
    
    backend_display = format_backend_name(sim_data["backend_name"])
    
    return {
        "logical_circuit_svg": circuit_to_svg(logical_qc),
        "physical_circuit_svg": circuit_to_svg(sim_data["physical_circuit"]),
        "zx_graphs": zx_data,
        "metrics": {
            "hellinger_fidelity": sim_data["hellinger_fidelity"],
            "counts_ideal": counts_ideal,
            "counts_noisy": counts_noisy,
            "backend": sim_data["backend_name"],
            "chart_title": f"Deutsch-Jozsa NISQ Degradation ({params.n_qubits} Qubits, {params.oracle_type.capitalize()} Oracle)",
            "legend_labels": ["Ideal Physical Simulation", f"Simulated {backend_display} Noise"],
            "colors": ["#2f4b7c", "#f95d6a"]
        }
    }

@app.post("/algorithms/grover")
async def execute_grover(params: GroverParams):
    logical_qc = build_grover_circuit(params.n_qubits, params.marked_state)
    sim_data = run_nisq_simulation(logical_qc, params.backend_name)
    zx_data = generate_zx_graphs(
        sim_data["physical_circuit"], 
        params.target_noisy_qubit, 
        Fraction(params.phase_drift).limit_denominator()
    )
    
    # Pad counts for the full noise floor view
    counts_ideal = pad_counts(sim_data["counts_ideal"], params.n_qubits)
    counts_noisy = pad_counts(sim_data["counts_noisy"], params.n_qubits)
    
    backend_display = format_backend_name(sim_data["backend_name"])
    
    return {
        "logical_circuit_svg": circuit_to_svg(logical_qc),
        "physical_circuit_svg": circuit_to_svg(sim_data["physical_circuit"]),
        "zx_graphs": zx_data,
        "metrics": {
            "hellinger_fidelity": sim_data["hellinger_fidelity"],
            "counts_ideal": counts_ideal,
            "counts_noisy": counts_noisy,
            "backend": sim_data["backend_name"],
            "chart_title": f"Grover's Algorithm NISQ Degradation ({params.n_qubits} Qubits, Target |{params.marked_state}>)",
            "legend_labels": ["Ideal Physical Simulation", f"Simulated {backend_display} Noise"],
            "colors": ["#2f4b7c", "#f95d6a"]
        }
    }

@app.post("/algorithms/qaoa")
async def execute_qaoa(params: QAOAParams):
    # Convert edges from List[List[int]] to List[Tuple[int, int]]
    edges = [tuple(e) for e in params.edges]
    logical_qc = build_qaoa_circuit(params.n_qubits, params.p_layers, edges, params.gamma, params.beta)
    sim_data = run_nisq_simulation(logical_qc, params.backend_name)
    zx_data = generate_zx_graphs(
        sim_data["physical_circuit"], 
        params.target_noisy_qubit, 
        Fraction(params.phase_drift).limit_denominator()
    )
    
    # Pad counts for the full noise floor view
    counts_ideal = pad_counts(sim_data["counts_ideal"], params.n_qubits)
    counts_noisy = pad_counts(sim_data["counts_noisy"], params.n_qubits)
    
    backend_display = format_backend_name(sim_data["backend_name"])
    
    return {
        "logical_circuit_svg": circuit_to_svg(logical_qc),
        "physical_circuit_svg": circuit_to_svg(sim_data["physical_circuit"]),
        "zx_graphs": zx_data,
        "metrics": {
            "hellinger_fidelity": sim_data["hellinger_fidelity"],
            "counts_ideal": counts_ideal,
            "counts_noisy": counts_noisy,
            "backend": sim_data["backend_name"],
            "chart_title": f"QAOA NISQ Degradation (Max-Cut, p={params.p_layers})",
            "legend_labels": ["Ideal Physical Simulation", f"Simulated {backend_display} Noise"],
            "colors": ["#2f4b7c", "#f95d6a"]
        }
    }

@app.post("/algorithms/custom")
async def execute_custom(params: CustomParams):
    try:
        # Load the circuit from the provided QASM string
        logical_qc = qasm2.loads(params.qasm)
        
        sim_data = run_nisq_simulation(logical_qc, params.backend_name)
        zx_data = generate_zx_graphs(
            sim_data["physical_circuit"], 
            params.target_noisy_qubit, 
            Fraction(params.phase_drift).limit_denominator()
        )
        
        # For custom, we only show output states (no padding)
        # Use default theme colors
        return {
            "logical_circuit_svg": circuit_to_svg(logical_qc),
            "physical_circuit_svg": circuit_to_svg(sim_data["physical_circuit"]),
            "zx_graphs": zx_data,
            "metrics": {
                "hellinger_fidelity": sim_data["hellinger_fidelity"],
                "counts_ideal": sim_data["counts_ideal"],
                "counts_noisy": sim_data["counts_noisy"],
                "backend": sim_data["backend_name"],
                "chart_title": "Custom Circuit Output State Distribution",
                "legend_labels": ["Ideal Simulation", "Hardware Noise Simulation"],
                "colors": ["var(--primary)", "var(--secondary)"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid QASM: {str(e)}")
