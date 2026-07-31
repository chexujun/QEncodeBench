from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 3-coloring on 6-vertex graph.
    
    Applies phase -1 iff all edges have endpoints with different colors.
    Color code: c = b0 + 2*b1 (mod 3), where b0 = problem_qubits[2v], b1 = problem_qubits[2v+1].
    """
    edges = [(0, 3), (0, 5), (1, 5), (2, 3), (2, 4), (2, 5), (4, 5)]
    
    # Accumulate "same_color" status for all edges into ancilla[0]
    # For each edge, flip ancilla[0] if the edge has same-colored endpoints
    for u, v in edges:
        add_if_same_color(qc, problem_qubits, u, v, ancilla_qubits[0])
    
    # Negate: ancilla[0] becomes 1 iff all edges are valid (all different colors)
    qc.x(ancilla_qubits[0])
    
    # Apply Z gate: adds -1 phase when ancilla[0] = 1
    qc.z(ancilla_qubits[0])
    
    # Uncompute in reverse: restore ancilla[0] to |0>
    qc.x(ancilla_qubits[0])
    for u, v in reversed(edges):
        add_if_same_color(qc, problem_qubits, u, v, ancilla_qubits[0])

def add_if_same_color(qc, problem_qubits, u, v, out):
    """Flip out (apply X) iff vertices u and v have the same color."""
    b0u = problem_qubits[2*u]
    b1u = problem_qubits[2*u+1]
    b0v = problem_qubits[2*v]
    b1v = problem_qubits[2*v+1]
    
    # Vertices have same color in exactly 6 cases:
    # Both color 0: (0,0)+(0,0), (0,0)+(1,1), (1,1)+(0,0), (1,1)+(1,1)
    # Both color 1: (1,0)+(1,0)
    # Both color 2: (0,1)+(0,1)
    invalid_configs = [
        (0, 0, 0, 0),
        (0, 0, 1, 1),
        (1, 1, 0, 0),
        (1, 1, 1, 1),
        (1, 0, 1, 0),
        (0, 1, 0, 1),
    ]
    
    for b0u_val, b1u_val, b0v_val, b1v_val in invalid_configs:
        # Build control qubits for this configuration
        controls = []
        negate_list = []
        
        for q, expected in [(b0u, b0u_val), (b1u, b1u_val), (b0v, b0v_val), (b1v, b1v_val)]:
            if expected == 0:
                # Control on q=0 requires negation
                negate_list.append(q)
                controls.append(q)
                negate_list.append(q)
            else:
                controls.append(q)
        
        # Apply NOT to qubits that need control on 0
        for q in negate_list:
            qc.x(q)
        
        # Apply multi-controlled X gate
        if len(controls) <= 2:
            if len(controls) == 1:
                qc.cx(controls[0], out)
            else:
                qc.ccx(controls[0], controls[1], out)
        else:
            qc.append(MCXGate(len(controls)), controls + [out])
        
        # Restore qubits
        for q in negate_list:
            qc.x(q)
