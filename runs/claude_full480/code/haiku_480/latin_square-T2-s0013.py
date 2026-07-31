from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for 3x3 Latin square completion.
    
    Marks the unique basis state that decodes to a valid Latin square
    completion of the partially filled grid:
      1 . .
      2 0 .
      0 1 2
    
    The unique solution is:
      1 2 0
      2 0 1
      0 1 2
    
    Free cells are at (0,1), (0,2), (1,2) with encoding:
    - free[0] must be 2 (code 10: q0=0, q1=1)
    - free[1] must be 0 (code 00: q2=0, q3=0)
    - free[2] must be 1 (code 01: q4=1, q5=0)
    """
    q0, q1, q2, q3, q4, q5 = problem_qubits
    anc = ancilla_qubits
    
    # Ancilla allocation for compute-phase-uncompute discipline
    a_c1 = anc[0]      # Constraint 1: q0=0 AND q1=1
    a_c2 = anc[1]      # Constraint 2: q2=0 AND q3=0
    a_c3 = anc[2]      # Constraint 3: q4=1 AND q5=0
    a_and12 = anc[3]   # Temporary: c1 AND c2
    a_result = anc[4]  # Final: c1 AND c2 AND c3
    
    # === COMPUTE ===
    
    # Constraint 1: (NOT q0) AND q1
    qc.x(q0)
    qc.ccx(q0, q1, a_c1)
    qc.x(q0)
    
    # Constraint 2: (NOT q2) AND (NOT q3)
    qc.x(q2)
    qc.x(q3)
    qc.ccx(q2, q3, a_c2)
    qc.x(q3)
    qc.x(q2)
    
    # Constraint 3: q4 AND (NOT q5)
    qc.x(q5)
    qc.ccx(q4, q5, a_c3)
    qc.x(q5)
    
    # AND all constraints together
    qc.ccx(a_c1, a_c2, a_and12)
    qc.ccx(a_and12, a_c3, a_result)
    
    # === PHASE FLIP ===
    qc.z(a_result)
    
    # === UNCOMPUTE ===
    qc.ccx(a_and12, a_c3, a_result)
    qc.ccx(a_c1, a_c2, a_and12)
    
    qc.x(q5)
    qc.ccx(q4, q5, a_c3)
    qc.x(q5)
    
    qc.x(q2)
    qc.x(q3)
    qc.ccx(q2, q3, a_c2)
    qc.x(q3)
    qc.x(q2)
    
    qc.x(q0)
    qc.ccx(q0, q1, a_c1)
    qc.x(q0)
