from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4, q5, q6, q7 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Compute constraint 1: cell 0 value = 1 (code 01)
    # Need: q0=1 AND q1=0
    qc.x(q1)
    qc.ccx(q0, q1, a0)
    qc.x(q1)
    
    # Compute constraint 2: cell 1 value = 0 (code 00 or 11)
    # Need: q2==q3 (XNOR), i.e., NOT(q2 XOR q3)
    qc.cx(q2, a1)
    qc.cx(q3, a1)
    qc.x(a1)
    
    # Compute constraint 3: cell 2 value = 0 (code 00 or 11)
    # Need: q4==q5 (XNOR), i.e., NOT(q4 XOR q5)
    qc.cx(q4, a2)
    qc.cx(q5, a2)
    qc.x(a2)
    
    # Compute constraint 4: cell 3 value = 2 (code 10)
    # Need: q6=0 AND q7=1
    qc.x(q6)
    qc.ccx(q6, q7, a3)
    qc.x(q6)
    
    # AND all constraints: apply phase only when all are true
    qc.mcx([a0, a1, a2, a3], a4)
    qc.z(a4)
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Uncompute all constraints in reverse
    qc.x(q6)
    qc.ccx(q6, q7, a3)
    qc.x(q6)
    
    qc.x(a2)
    qc.cx(q5, a2)
    qc.cx(q4, a2)
    
    qc.x(a1)
    qc.cx(q3, a1)
    qc.cx(q2, a1)
    
    qc.x(q1)
    qc.ccx(q0, q1, a0)
    qc.x(q1)
