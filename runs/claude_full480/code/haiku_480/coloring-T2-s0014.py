from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for graph 3-coloring: marks valid colorings where every edge
    connects vertices of different colors.
    
    Encoding: vertex v uses problem_qubits[2*v] (b0) and problem_qubits[2*v+1] (b1).
    Color code c = b0 + 2*b1 decodes to:
      00->0, 01->1, 10->2, 11->0 (surjective, with 0 appearing twice).
    
    Same-color predicate: vertices u,v have same color iff
      (b0_u == b0_v AND b1_u == b1_v) OR (parity_u == 0 AND parity_v == 0)
      where parity_x = b0_x XOR b1_x.
    
    Strategy: compute-phase-uncompute with accumulation.
    Maintains a result qubit initialized to 1, set to 0 if any edge is monochromatic.
    """
    
    edges = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
    
    # Allocate ancillas
    result = ancilla_qubits[6]
    parity_u = ancilla_qubits[0]
    parity_v = ancilla_qubits[1]
    b0_eq = ancilla_qubits[2]
    b1_eq = ancilla_qubits[3]
    term1 = ancilla_qubits[4]
    term2 = ancilla_qubits[5]
    
    def compute_edge(u, v):
        """Compute monochromatic flags into term1 and term2."""
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        # Compute parity_u = b0_u XOR b1_u
        qc.cx(b0_u, parity_u)
        qc.cx(b1_u, parity_u)
        
        # Compute parity_v = b0_v XOR b1_v
        qc.cx(b0_v, parity_v)
        qc.cx(b1_v, parity_v)
        
        # Compute b0_eq = (b0_u == b0_v) using XNOR
        qc.cx(b0_u, b0_eq)
        qc.cx(b0_v, b0_eq)
        qc.x(b0_eq)
        
        # Compute b1_eq = (b1_u == b1_v)
        qc.cx(b1_u, b1_eq)
        qc.cx(b1_v, b1_eq)
        qc.x(b1_eq)
        
        # term1: both vertices have same bits (00/01/10/11)
        qc.ccx(b0_eq, b1_eq, term1)
        
        # term2: both vertices have even parity (both in {00, 11})
        qc.x(parity_u)
        qc.x(parity_v)
        qc.ccx(parity_u, parity_v, term2)
        qc.x(parity_u)
        qc.x(parity_v)
    
    def uncompute_edge(u, v):
        """Reverse computation: restore all ancillas to 0."""
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.x(parity_u)
        qc.x(parity_v)
        qc.ccx(parity_u, parity_v, term2)
        qc.x(parity_u)
        qc.x(parity_v)
        
        qc.ccx(b0_eq, b1_eq, term1)
        
        qc.x(b1_eq)
        qc.cx(b1_v, b1_eq)
        qc.cx(b1_u, b1_eq)
        
        qc.x(b0_eq)
        qc.cx(b0_v, b0_eq)
        qc.cx(b0_u, b0_eq)
        
        qc.cx(b1_v, parity_v)
        qc.cx(b0_v, parity_v)
        
        qc.cx(b1_u, parity_u)
        qc.cx(b0_u, parity_u)
    
    # Initialize result to |1>
    qc.x(result)
    
    # Forward pass: for each edge, compute monochromatic flags and update result
    for u, v in edges:
        compute_edge(u, v)
        # result AND= NOT(term1 OR term2) via: result AND= NOT(term1) AND NOT(term2)
        qc.ccx(result, term1, result)
        qc.ccx(result, term2, result)
        uncompute_edge(u, v)
    
    # Apply phase: Z gate if result == 1 (all edges are good)
    qc.z(result)
    
    # Backward pass: mirror the forward pass to uncompute and restore result
    for u, v in reversed(edges):
        compute_edge(u, v)
        # Undo result updates in reverse order
        qc.ccx(result, term2, result)
        qc.ccx(result, term1, result)
        uncompute_edge(u, v)
    
    # Uninitialize result back to |0>
    qc.x(result)
