from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits[0:4]
    a0, a1, a2 = ancilla_qubits[0:3]
    
    # The unique valid Latin square requires:
    # - Free cell 0 (at row 0, col 1) = 2  →  code 10  →  q0=0, q1=1
    # - Free cell 1 (at row 2, col 1) = 0  →  code 00 or 11  →  q2==q3
    # Predicate: (NOT q0) AND q1 AND (q2 XNOR q3)
    
    # Compute (NOT q0) AND q1 into a0
    qc.x(q0)
    qc.ccx(q0, q1, a0)
    qc.x(q0)
    
    # Compute (q2 XNOR q3) into a1
    qc.cx(q2, a1)
    qc.cx(q3, a1)
    qc.x(a1)
    
    # Compute a0 AND a1 into a2
    qc.ccx(a0, a1, a2)
    
    # Apply phase
    qc.z(a2)
    
    # Uncompute
    qc.ccx(a0, a1, a2)
    qc.x(a1)
    qc.cx(q3, a1)
    qc.cx(q2, a1)
    qc.x(q0)
    qc.ccx(q0, q1, a0)
    qc.x(q0)
