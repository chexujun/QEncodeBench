from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    """
    Oracle for 3-coloring on a 6-vertex graph.
    Applies phase -1 to invalid colorings (where at least one edge has same-colored endpoints).
    """
    edges = [(0, 4), (0, 5), (1, 3), (1, 5), (2, 5), (3, 4), (3, 5)]
    
    invalid = ancilla_qubits[0]  # accumulator for "any edge violated"
    t1 = ancilla_qubits[1]        # working registers
    t2 = ancilla_qubits[2]
    t3 = ancilla_qubits[3]
    
    for u, v in edges:
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        
        # Check all three color-class violations for this edge
        # Violation 1: both decode to color 0 (codes 00 or 11)
        # Color 0 iff b0 XNOR b1, i.e., NOT(b0 XOR b1)
        qc.cx(b0_u, t1)
        qc.cx(b1_u, t1)
        qc.x(t1)  # t1 = NOT(b0_u XOR b1_u)
        
        qc.cx(b0_v, t2)
        qc.cx(b1_v, t2)
        qc.x(t2)  # t2 = NOT(b0_v XOR b1_v)
        
        qc.ccx(t1, t2, t3)  # t3 = 1 iff both color 0
        
        # OR t3 into invalid: invalid = NOT(NOT invalid AND NOT t3)
        qc.x(invalid)
        qc.x(t3)
        qc.ccx(invalid, t3, t1)
        qc.x(t3)
        qc.x(invalid)
        qc.x(t1)
        qc.cx(t1, invalid)
        qc.x(t1)
        
        # Uncompute t3
        qc.ccx(t1, t2, t3)
        
        # Restore t2
        qc.x(t2)
        qc.cx(b1_v, t2)
        qc.cx(b0_v, t2)
        
        # Restore t1
        qc.x(t1)
        qc.cx(b1_u, t1)
        qc.cx(b0_u, t1)
        
        # Violation 2: both decode to color 1 (code 01)
        # Color 1 iff b0=1 AND b1=0
        qc.x(b1_u)
        qc.x(b1_v)
        
        qc.ccx(b0_u, b1_u, t1)  # t1 = b0_u AND NOT(b1_u)
        qc.ccx(b0_v, b1_v, t2)  # t2 = b0_v AND NOT(b1_v)
        qc.ccx(t1, t2, t3)  # t3 = 1 iff both color 1
        
        # OR into invalid
        qc.x(invalid)
        qc.x(t3)
        qc.ccx(invalid, t3, t1)
        qc.x(t3)
        qc.x(invalid)
        qc.x(t1)
        qc.cx(t1, invalid)
        qc.x(t1)
        
        # Uncompute
        qc.ccx(t1, t2, t3)
        qc.x(b1_v)
        qc.x(b1_u)
        qc.ccx(b0_v, b1_v, t2)
        qc.ccx(b0_u, b1_u, t1)
        qc.x(b1_v)
        qc.x(b1_u)
        
        # Violation 3: both decode to color 2 (code 10)
        # Color 2 iff b0=0 AND b1=1
        qc.x(b0_u)
        qc.x(b0_v)
        
        qc.ccx(b0_u, b1_u, t1)  # t1 = NOT(b0_u) AND b1_u
        qc.ccx(b0_v, b1_v, t2)  # t2 = NOT(b0_v) AND b1_v
        qc.ccx(t1, t2, t3)  # t3 = 1 iff both color 2
        
        # OR into invalid
        qc.x(invalid)
        qc.x(t3)
        qc.ccx(invalid, t3, t1)
        qc.x(t3)
        qc.x(invalid)
        qc.x(t1)
        qc.cx(t1, invalid)
        qc.x(t1)
        
        # Uncompute
        qc.ccx(t1, t2, t3)
        qc.x(b0_v)
        qc.x(b0_u)
        qc.ccx(b0_v, b1_v, t2)
        qc.ccx(b0_u, b1_u, t1)
        qc.x(b0_v)
        qc.x(b0_u)
    
    # Apply Z phase: -1 if any edge is violated
    qc.z(invalid)
