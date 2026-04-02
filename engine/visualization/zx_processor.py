import pyzx as zx
from qiskit import qasm2
import matplotlib.pyplot as plt
import io

def graph_to_svg(g):
    """Converts a PyZX graph to an SVG string using matplotlib backend."""
    # We use a large enough figsize to avoid overlapping
    fig = zx.draw_matplotlib(g, figsize=(12, 4))
    buf = io.StringIO()
    fig.savefig(buf, format='svg', bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()

def generate_zx_graphs(physical_circuit, target_noisy_qubit, systematic_phase_drift):
    """Generates Ideal, Noisy, and Propagated ZX graphs from a Qiskit circuit."""
    
    # 1. Prepare Circuit for PyZX
    pyzx_qc = physical_circuit.copy()
    pyzx_qc._layout = None
    pyzx_qc.remove_final_measurements()
    
    # Convert to QASM and then PyZX Graph
    qasm_str = qasm2.dumps(pyzx_qc)
    g_ideal = zx.Circuit.from_qasm(qasm_str).to_graph()
    
    # 2. Inject Systematic Noise
    g_noisy = g_ideal.copy()
    noise_err = g_noisy.add_vertex(
        zx.VertexType.Z, 
        qubit=target_noisy_qubit, 
        row=1, 
        phase=systematic_phase_drift
    )

    edges = list(g_noisy.edges())
    for e in edges:
        s, t = g_noisy.edge_st(e)
        if g_noisy.qubit(s) == target_noisy_qubit and g_noisy.qubit(t) == target_noisy_qubit:
            g_noisy.remove_edge(e)
            g_noisy.add_edge((s, noise_err))
            g_noisy.add_edge((noise_err, t))
            break
            
    # 3. Simplify to observe Error Propagation
    g_propagated = g_noisy.copy()
    zx.simplify.spider_simp(g_propagated)
    
    # Convert graphs to SVG strings for the frontend
    return {
        "ideal": graph_to_svg(g_ideal),
        "noisy": graph_to_svg(g_noisy),
        "propagated": graph_to_svg(g_propagated)
    }
