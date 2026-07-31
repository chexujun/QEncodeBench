from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1 = problem_qubits[0], problem_qubits[1]
    q2, q3 = problem_qubits[2], problem_qubits[3]
    q4, q5 = problem_qubits[4], problem_qubits[5]
    q6, q7 = problem_qubits[6], problem_qubits[7]
    
    a0, a1, a2, a3, a4, a5 = ancilla_qubits[0:6]
    
    # Compute constraint s0: NOT(q0 XOR q1) - free cell 0 must decode to 0
    qc.cx(q0, a0)
    qc.cx(q1, a0)
    qc.x(a0)
    
    # Compute constraint s1: NOT(q2 XOR q3) - free cell 1 must decode to 0
    qc.cx(q2, a1)
    qc.cx(q3, a1)
    qc.x(a1)
    
    # Compute constraint s2: (NOT q4) AND q5 - free cell 2 must decode to 2
    qc.x(q4)
    qc.ccx(q4, q5, a2)
    qc.x(q4)
    
    # Compute constraint s3: q6 AND (NOT q7) - free cell 3 must decode to 1
    qc.x(q7)
    qc.ccx(q6, q7, a3)
    qc.x(q7)
    
    # Compute AND of all constraints: a4 = a0 AND a1 AND a2 AND a3
    qc.ccx(a0, a1, a4)           # a4 = a0 AND a1
    qc.ccx(a4, a2, a5)           # a5 = (a0 AND a1) AND a2
    qc.ccx(a5, a3, a4)           # a4 = overall result
    
    # Apply phase -1 if all constraints satisfied
    qc.z(a4)
    
    # Uncompute AND of constraints (reverse order)
    qc.ccx(a5, a3, a4)
    qc.ccx(a4, a2, a5)
    qc.ccx(a0, a1, a4)
    
    # Uncompute constraint s3
    qc.x(q7)
    qc.ccx(q6, q7, a3)
    qc.x(q7)
    
    # Uncompute constraint s2
    qc.x(q4)
    qc.ccx(q4, q5, a2)
    qc.x(q4)
    
    # Uncompute constraint s1
    qc.x(a1)
    qc.cx(q3, a1)
    qc.cx(q2, a1)
    
    # Uncompute constraint s0
    qc.x(a0)
    qc.cx(q1, a0)
    qc.cx(q0, a0)
