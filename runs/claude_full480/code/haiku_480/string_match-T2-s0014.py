from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s = problem_qubits
    a0, a1, a2, a_or = ancilla_qubits[0:4]
    
    # Compute offset 0 match: s[0]=1, s[1]=0, s[2]=1
    qc.x(s[1])
    qc.ccx(s[0], s[2], a0)
    qc.ccx(s[1], a0, a0)
    qc.x(s[1])
    
    # Compute offset 1 match: s[1]=1, s[2]=0, s[3]=1
    qc.x(s[2])
    qc.ccx(s[1], s[3], a1)
    qc.ccx(s[2], a1, a1)
    qc.x(s[2])
    
    # Compute offset 2 match: s[2]=1, s[3]=0, s[4]=1
    qc.x(s[3])
    qc.ccx(s[2], s[4], a2)
    qc.ccx(s[3], a2, a2)
    qc.x(s[3])
    
    # Compute OR: a_or = a0 OR a1 OR a2
    # using a_or = NOT(NOT a0 AND NOT a1 AND NOT a2)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.ccx(a0, a1, a_or)
    qc.ccx(a2, a_or, a_or)
    qc.x(a_or)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Apply phase
    qc.z(a_or)
    
    # Uncompute OR
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a_or)
    qc.ccx(a2, a_or, a_or)
    qc.ccx(a0, a1, a_or)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute offset 2
    qc.x(s[3])
    qc.ccx(s[3], a2, a2)
    qc.ccx(s[2], s[4], a2)
    qc.x(s[3])
    
    # Uncompute offset 1
    qc.x(s[2])
    qc.ccx(s[2], a1, a1)
    qc.ccx(s[1], s[3], a1)
    qc.x(s[2])
    
    # Uncompute offset 0
    qc.x(s[1])
    qc.ccx(s[1], a0, a0)
    qc.ccx(s[0], s[2], a0)
    qc.x(s[1])
