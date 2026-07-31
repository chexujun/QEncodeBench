from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0,1), (0,2), (1,2), (1,3), (1,4), (2,3), (3,4)]
    
    edge_violations = ancilla_qubits[:7]
    
    # Compute violation (same color) for each edge
    for edge_idx, (u, v) in enumerate(edges):
        b0u = problem_qubits[2*u]
        b1u = problem_qubits[2*u+1]
        b0v = problem_qubits[2*v]
        b1v = problem_qubits[2*v+1]
        
        compute_colors_equal(qc, b0u, b1u, b0v, b1v, edge_violations[edge_idx])
    
    # Negate all violation qubits (so valid colorings have all 1s)
    for v in edge_violations:
        qc.x(v)
    
    # Apply multi-controlled phase: phase -1 when all violations are 0 (all negated are 1)
    qc.mcp(pi, edge_violations)
    
    # Undo X gates
    for v in edge_violations:
        qc.x(v)
    
    # Uncompute violations in reverse order
    for edge_idx in range(len(edges) - 1, -1, -1):
        u, v = edges[edge_idx]
        b0u = problem_qubits[2*u]
        b1u = problem_qubits[2*u+1]
        b0v = problem_qubits[2*v]
        b1v = problem_qubits[2*v+1]
        
        uncompute_colors_equal(qc, b0u, b1u, b0v, b1v, edge_violations[edge_idx])


def compute_colors_equal(qc, b0u, b1u, b0v, b1v, target):
    # Compute 1 into target iff colors of two vertices are equal
    # Color mapping: code (b0,b1) -> color value (code % 3)
    # 00->0, 01->1, 10->2, 11->0 (surjective)
    # Colors equal for: (0,0,0,0), (0,0,1,1), (1,1,0,0), (1,1,1,1), (1,0,1,0), (0,1,0,1)
    
    # Pattern: both color 0 - code pair (00 or 11, 00 or 11)
    qc.x(b0u)
    qc.x(b1u)
    qc.x(b0v)
    qc.x(b1v)
    qc.mcx([b0u, b1u, b0v, b1v], target)  # (0,0,0,0)
    qc.x(b1v)
    qc.x(b0v)
    qc.x(b1u)
    qc.x(b0u)
    
    qc.x(b0u)
    qc.x(b1u)
    qc.mcx([b0u, b1u, b0v, b1v], target)  # (0,0,1,1)
    qc.x(b1u)
    qc.x(b0u)
    
    qc.x(b0v)
    qc.x(b1v)
    qc.mcx([b0u, b1u, b0v, b1v], target)  # (1,1,0,0)
    qc.x(b1v)
    qc.x(b0v)
    
    qc.mcx([b0u, b1u, b0v, b1v], target)  # (1,1,1,1)
    
    # Pattern: both color 1 - code pair (01, 01)
    qc.x(b1u)
    qc.x(b1v)
    qc.mcx([b0u, b1u, b0v, b1v], target)  # (1,0,1,0)
    qc.x(b1v)
    qc.x(b1u)
    
    # Pattern: both color 2 - code pair (10, 10)
    qc.x(b0u)
    qc.x(b0v)
    qc.mcx([b0u, b1u, b0v, b1v], target)  # (0,1,0,1)
    qc.x(b0v)
    qc.x(b0u)


def uncompute_colors_equal(qc, b0u, b1u, b0v, b1v, target):
    # Reverse of compute_colors_equal
    
    qc.x(b0u)
    qc.x(b0v)
    qc.mcx([b0u, b1u, b0v, b1v], target)
    qc.x(b0v)
    qc.x(b0u)
    
    qc.x(b1u)
    qc.x(b1v)
    qc.mcx([b0u, b1u, b0v, b1v], target)
    qc.x(b1v)
    qc.x(b1u)
    
    qc.mcx([b0u, b1u, b0v, b1v], target)
    
    qc.x(b0v)
    qc.x(b1v)
    qc.mcx([b0u, b1u, b0v, b1v], target)
    qc.x(b1v)
    qc.x(b0v)
    
    qc.x(b0u)
    qc.x(b1u)
    qc.mcx([b0u, b1u, b0v, b1v], target)
    qc.x(b1u)
    qc.x(b0u)
    
    qc.x(b0u)
    qc.x(b1u)
    qc.x(b0v)
    qc.x(b1v)
    qc.mcx([b0u, b1u, b0v, b1v], target)
    qc.x(b1v)
    qc.x(b0v)
    qc.x(b1u)
    qc.x(b0u)
