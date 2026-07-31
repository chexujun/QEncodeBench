from qiskit import QuantumCircuit
from qiskit.circuit import QuantumRegister

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 3-coloring on a 5-vertex graph.
    f(x) = 1 iff all edges connect vertices of different colors.
    """
    # Edges: (0,1), (0,3), (0,4), (1,2), (1,4), (2,4)
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (2, 4)]
    
    # Ancilla allocation: ancilla_qubits[0:6] store same_color for each edge
    # ancilla_qubits[6] is used as temporary during OR computation
    
    # Compute same_color(v, u) for each edge into ancilla 0-5
    for edge_idx, (v, u) in enumerate(edges):
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        same_color_anc = ancilla_qubits[edge_idx]
        
        _compute_same_color(qc, b0_v, b1_v, b0_u, b1_u, same_color_anc)
    
    # Compute violation = OR of all same_color values
    violation = ancilla_qubits[6]
    same_color_list = ancilla_qubits[0:6]
    
    # violation = NOT(AND of negated same_color bits)
    for bit in same_color_list:
        qc.x(bit)
    qc.mcx(same_color_list, violation)
    for bit in same_color_list:
        qc.x(bit)
    qc.x(violation)
    
    # Apply phase -1 if violation == 0 (no violations means f(x) = 1)
    qc.z(violation)
    
    # Uncompute violation
    qc.x(violation)
    for bit in same_color_list:
        qc.x(bit)
    qc.mcx(same_color_list, violation)
    for bit in same_color_list:
        qc.x(bit)
    
    # Uncompute same_color values
    for edge_idx, (v, u) in enumerate(edges):
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        same_color_anc = ancilla_qubits[edge_idx]
        
        _uncompute_same_color(qc, b0_v, b1_v, b0_u, b1_u, same_color_anc)

def _compute_same_color(qc, b0_v, b1_v, b0_u, b1_u, result):
    """
    Compute: result = 1 iff color(v) == color(u).
    same_color cases (of 16 total): (0,0,0,0), (0,0,1,1), (0,1,0,1), (1,0,1,0), (1,1,0,0), (1,1,1,1)
    """
    # Case (0,0,0,0): all bits 0
    qc.x(b0_v)
    qc.x(b1_v)
    qc.x(b0_u)
    qc.x(b1_u)
    qc.mcx([b0_v, b1_v, b0_u, b1_u], result)
    qc.x(b0_v)
    qc.x(b1_v)
    qc.x(b0_u)
    qc.x(b1_u)
    
    # Case (0,0,1,1): b0_v=0, b1_v=0, b0_u=1, b1_u=1
    qc.x(b0_v)
    qc.x(b1_v)
    qc.mcx([b0_v, b1_v, b0_u, b1_u], result)
    qc.x(b0_v)
    qc.x(b1_v)
    
    # Case (0,1,0,1): b0_v=0, b1_v=1, b0_u=0, b1_u=1
    qc.x(b0_v)
    qc.x(b0_u)
    qc.mcx([b0_v, b1_v, b0_u, b1_u], result)
    qc.x(b0_v)
    qc.x(b0_u)
    
    # Case (1,0,1,0): b0_v=1, b1_v=0, b0_u=1, b1_u=0
    qc.x(b1_v)
    qc.x(b1_u)
    qc.mcx([b0_v, b1_v, b0_u, b1_u], result)
    qc.x(b1_v)
    qc.x(b1_u)
    
    # Case (1,1,0,0): b0_v=1, b1_v=1, b0_u=0, b1_u=0
    qc.x(b0_u)
    qc.x(b1_u)
    qc.mcx([b0_v, b1_v, b0_u, b1_u], result)
    qc.x(b0_u)
    qc.x(b1_u)
    
    # Case (1,1,1,1): all bits 1
    qc.mcx([b0_v, b1_v, b0_u, b1_u], result)

def _uncompute_same_color(qc, b0_v, b1_v, b0_u, b1_u, result):
    """Reverse of _compute_same_color (gates are self-inverse)."""
    _compute_same_color(qc, b0_v, b1_v, b0_u, b1_u, result)
