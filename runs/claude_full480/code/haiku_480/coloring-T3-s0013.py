from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    """
    Grover phase oracle for graph coloring: marks valid 3-colorings where all edges connect different colors.
    
    For each 2-qubit code (b0, b1) per vertex, colors decode as: 00→0, 01→1, 10→2, 11→0.
    An edge is valid (constraint satisfied) iff its endpoints have different decoded colors.
    The oracle applies phase -1 to states where ALL edges are valid.
    
    Strategy: For each edge, compute whether colors are the same (violation).
    Accumulate violations in ancilla[0]; apply phase if no violations occurred.
    """
    edges = [(0,2), (0,3), (0,4), (1,2), (1,3), (1,4), (2,3), (3,4)]
    
    v_acc = ancilla_qubits[0]   # Violation accumulator
    t_pu = ancilla_qubits[1]    # parity_u = problem_qubits[2u] XOR problem_qubits[2u+1]
    t_pv = ancilla_qubits[2]    # Temporary (used for AND result)
    t_pxor = ancilla_qubits[3]  # parity_u XOR parity_v (directly from 4 problem qubits)
    t_bxor = ancilla_qubits[4]  # b0_u XOR b0_v
    
    # Key insight: colors at vertices u,v are the same iff
    # NOT(parity_u XOR parity_v) AND NOT(parity_u AND (b0_u XOR b0_v))
    # This checks: (1) both have same parity, (2) if odd parity, same low bit.
    
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute parity_u = u0 XOR u1
        qc.cx(u0, t_pu)
        qc.cx(u1, t_pu)
        
        # Compute parity_xor = u0 XOR u1 XOR v0 XOR v1
        qc.cx(u0, t_pxor)
        qc.cx(u1, t_pxor)
        qc.cx(v0, t_pxor)
        qc.cx(v1, t_pxor)
        
        # Compute b_xor = u0 XOR v0
        qc.cx(u0, t_bxor)
        qc.cx(v0, t_bxor)
        
        # Compute t_pu AND t_bxor into t_pv (initially 0)
        qc.ccx(t_pu, t_bxor, t_pv)
        
        # Negate t_pxor to represent NOT(parity_u XOR parity_v)
        qc.x(t_pxor)
        
        # Negate t_pv to represent NOT(parity_u AND b_xor)
        qc.x(t_pv)
        
        # OR: set v_acc if both NOT(parity_xor) AND NOT(p_u AND b_xor) are 1
        # This marks a violation (colors same) in v_acc
        qc.ccx(t_pxor, t_pv, v_acc)
        
        # Uncompute all temporaries (reverse order)
        qc.x(t_pv)                             # Undo negate
        qc.ccx(t_pu, t_bxor, t_pv)             # Undo AND
        qc.x(t_pxor)                           # Undo negate
        qc.cx(v0, t_bxor)                      # Undo b_xor
        qc.cx(u0, t_bxor)
        qc.cx(v1, t_pxor)                      # Undo parity_xor
        qc.cx(v0, t_pxor)
        qc.cx(u1, t_pxor)
        qc.cx(u0, t_pxor)
        qc.cx(u1, t_pu)                        # Undo parity_u
        qc.cx(u0, t_pu)
    
    # Apply phase -1 if v_acc = 0 (all constraints satisfied, no violations)
    # X → flip to 1; Z → phase -1 on |1>; X → flip back to |0> with phase
    qc.x(v_acc)
    qc.z(v_acc)
    qc.x(v_acc)
