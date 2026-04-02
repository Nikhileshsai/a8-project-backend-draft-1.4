from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fractions import Fraction
import numpy as np
from qiskit import qasm2

# Engine Imports
from engine.algorithms.deutsch_jozsa import build_dj_circuit
from engine.algorithms.grover import build_grover_circuit
from engine.algorithms.qaoa import build_qaoa_circuit
from engine.visualization.zx_processor import generate_zx_graphs
from engine.simulators.qiskit_sim import run_nisq_simulation

app = FastAPI(title="NISQ Visualizer API")

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

class GroverParams(BaseModel):
    n_qubits: int
    marked_state: str
    target_noisy_qubit: int = 0
    phase_drift: float = 0.25

class QAOAParams(BaseModel):
    n_qubits: int
    p_layers: int
    edges: List[List[int]]
    gamma: float = np.pi / 3
    beta: float = np.pi / 4
    target_noisy_qubit: int = 0
    phase_drift: float = 0.25

@app.post("/algorithms/deutsch-jozsa")
async def execute_dj(params: DJParams):
    logical_qc = build_dj_circuit(params.n_qubits, params.oracle_type)
    sim_data = run_nisq_simulation(logical_qc)
    zx_data = generate_zx_graphs(
        sim_data["physical_circuit"], 
        params.target_noisy_qubit, 
        Fraction(params.phase_drift).limit_denominator()
    )
    
    return {
        "logical_circuit_qasm": qasm2.dumps(logical_qc),
        "physical_circuit_qasm": sim_data["physical_circuit_qasm"],
        "zx_graphs": zx_data,
        "metrics": {
            "hellinger_fidelity": sim_data["hellinger_fidelity"],
            "counts_ideal": sim_data["counts_ideal"],
            "counts_noisy": sim_data["counts_noisy"],
            "backend": sim_data["backend_name"]
        }
    }

@app.post("/algorithms/grover")
async def execute_grover(params: GroverParams):
    logical_qc = build_grover_circuit(params.n_qubits, params.marked_state)
    sim_data = run_nisq_simulation(logical_qc)
    zx_data = generate_zx_graphs(
        sim_data["physical_circuit"], 
        params.target_noisy_qubit, 
        Fraction(params.phase_drift).limit_denominator()
    )
    
    return {
        "logical_circuit_qasm": qasm2.dumps(logical_qc),
        "physical_circuit_qasm": sim_data["physical_circuit_qasm"],
        "zx_graphs": zx_data,
        "metrics": {
            "hellinger_fidelity": sim_data["hellinger_fidelity"],
            "counts_ideal": sim_data["counts_ideal"],
            "counts_noisy": sim_data["counts_noisy"],
            "backend": sim_data["backend_name"]
        }
    }

@app.post("/algorithms/qaoa")
async def execute_qaoa(params: QAOAParams):
    # Convert edges from List[List[int]] to List[Tuple[int, int]]
    edges = [tuple(e) for e in params.edges]
    logical_qc = build_qaoa_circuit(params.n_qubits, params.p_layers, edges, params.gamma, params.beta)
    sim_data = run_nisq_simulation(logical_qc)
    zx_data = generate_zx_graphs(
        sim_data["physical_circuit"], 
        params.target_noisy_qubit, 
        Fraction(params.phase_drift).limit_denominator()
    )
    
    return {
        "logical_circuit_qasm": qasm2.dumps(logical_qc),
        "physical_circuit_qasm": sim_data["physical_circuit_qasm"],
        "zx_graphs": zx_data,
        "metrics": {
            "hellinger_fidelity": sim_data["hellinger_fidelity"],
            "counts_ideal": sim_data["counts_ideal"],
            "counts_noisy": sim_data["counts_noisy"],
            "backend": sim_data["backend_name"]
        }
    }
