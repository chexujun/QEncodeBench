from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4, q5 = problem_qubits[0:6]
    anc = ancilla_qubits
    
    # Compute constraint bits
    # C1: f0 ≠ 0 (value_0 != 0 iff q0 XOR q1 != 0)
    qc.cx(q0, anc[0])
    qc.cx(q1, anc[0])
    
    # C2: f0 ≠ 2 (NOT(q0=0 AND q1=1) = q0 OR NOT q1)
    qc.x(q0)
    qc.ccx(q0, q1, anc[1])
    qc.x(q0)
    qc.x(anc[1])
    
    # C3: f1 ≠ 0
    qc.cx(q2, anc[2])
    qc.cx(q3, anc[2])
    
    # C4: f1 ≠ 2
    qc.x(q2)
    qc.ccx(q2, q3, anc[3])
    qc.x(q2)
    qc.x(anc[3])
    
    # C5: f2 ≠ 0
    qc.cx(q4, anc[4])
    qc.cx(q5, anc[4])
    
    # C6: f0 ≠ f2: compute value_0 = value_2, then negate
    qc.cx(q0, anc[6])
    qc.cx(q1, anc[6])
    qc.x(anc[6])
    
    qc.cx(q4, anc[7])
    qc.cx(q5, anc[7])
    qc.x(anc[7])
    qc.ccx(anc[6], anc[7], anc[8])
    
    qc.x(q1)
    qc.ccx(q0, q1, anc[6])
    qc.x(q1)
    
    qc.x(q5)
    qc.ccx(q4, q5, anc[7])
    qc.x(q5)
    qc.ccx(anc[6], anc[7], anc[9])
    
    qc.x(q0)
    qc.ccx(q0, q1, anc[6])
    qc.x(q0)
    
    qc.x(q4)
    qc.ccx(q4, q5, anc[7])
    qc.x(q4)
    qc.ccx(anc[6], anc[7], anc[10])
    
    qc.x(anc[8])
    qc.x(anc[9])
    qc.ccx(anc[8], anc[9], anc[6])
    qc.x(anc[6])
    qc.x(anc[8])
    qc.x(anc[9])
    
    qc.x(anc[6])
    qc.x(anc[10])
    qc.ccx(anc[6], anc[10], anc[5])
    qc.x(anc[5])
    qc.x(anc[6])
    qc.x(anc[10])
    qc.x(anc[5])
    
    # C7: f1 ≠ f2
    qc.cx(q2, anc[6])
    qc.cx(q3, anc[6])
    qc.x(anc[6])
    
    qc.cx(q4, anc[7])
    qc.cx(q5, anc[7])
    qc.x(anc[7])
    qc.ccx(anc[6], anc[7], anc[8])
    
    qc.x(q3)
    qc.ccx(q2, q3, anc[6])
    qc.x(q3)
    
    qc.x(q5)
    qc.ccx(q4, q5, anc[7])
    qc.x(q5)
    qc.ccx(anc[6], anc[7], anc[9])
    
    qc.x(q2)
    qc.ccx(q2, q3, anc[6])
    qc.x(q2)
    
    qc.x(q4)
    qc.ccx(q4, q5, anc[7])
    qc.x(q4)
    qc.ccx(anc[6], anc[7], anc[10])
    
    qc.x(anc[8])
    qc.x(anc[9])
    qc.ccx(anc[8], anc[9], anc[7])
    qc.x(anc[7])
    qc.x(anc[8])
    qc.x(anc[9])
    
    qc.x(anc[7])
    qc.x(anc[10])
    qc.ccx(anc[7], anc[10], anc[6])
    qc.x(anc[6])
    qc.x(anc[7])
    qc.x(anc[10])
    qc.x(anc[6])
    
    # AND all constraints into ancilla[8]
    qc.ccx(anc[0], anc[1], anc[7])
    qc.ccx(anc[7], anc[2], anc[8])
    qc.ccx(anc[8], anc[3], anc[9])
    qc.ccx(anc[9], anc[4], anc[10])
    qc.ccx(anc[10], anc[5], anc[7])
    qc.ccx(anc[7], anc[6], anc[8])
    
    # Apply phase
    qc.z(anc[8])
    
    # Uncompute (reverse order)
    qc.ccx(anc[7], anc[6], anc[8])
    qc.ccx(anc[10], anc[5], anc[7])
    qc.ccx(anc[9], anc[4], anc[10])
    qc.ccx(anc[8], anc[3], anc[9])
    qc.ccx(anc[7], anc[2], anc[8])
    qc.ccx(anc[0], anc[1], anc[7])
    
    qc.x(anc[6])
    qc.x(anc[7])
    qc.x(anc[10])
    qc.ccx(anc[7], anc[10], anc[6])
    qc.x(anc[6])
    qc.x(anc[7])
    qc.x(anc[10])
    
    qc.x(q4)
    qc.ccx(q4, q5, anc[7])
    qc.x(q4)
    qc.x(q2)
    qc.ccx(q2, q3, anc[6])
    qc.x(q2)
    qc.ccx(anc[6], anc[7], anc[10])
    
    qc.x(q5)
    qc.ccx(q4, q5, anc[7])
    qc.x(q5)
    qc.x(q3)
    qc.ccx(q2, q3, anc[6])
    qc.x(q3)
    qc.ccx(anc[6], anc[7], anc[9])
    
    qc.cx(q4, anc[7])
    qc.cx(q5, anc[7])
    qc.x(anc[7])
    qc.cx(q2, anc[6])
    qc.cx(q3, anc[6])
    qc.x(anc[6])
    qc.ccx(anc[6], anc[7], anc[8])
    
    qc.x(anc[5])
    qc.x(anc[6])
    qc.x(anc[10])
    qc.ccx(anc[6], anc[10], anc[5])
    qc.x(anc[5])
    qc.x(anc[6])
    qc.x(anc[10])
    
    qc.x(q4)
    qc.ccx(q4, q5, anc[7])
    qc.x(q4)
    qc.x(q0)
    qc.ccx(q0, q1, anc[6])
    qc.x(q0)
    qc.ccx(anc[6], anc[7], anc[10])
    
    qc.x(q5)
    qc.ccx(q4, q5, anc[7])
    qc.x(q5)
    qc.x(q1)
    qc.ccx(q0, q1, anc[6])
    qc.x(q1)
    qc.ccx(anc[6], anc[7], anc[9])
    
    qc.cx(q4, anc[7])
    qc.cx(q5, anc[7])
    qc.x(anc[7])
    qc.cx(q0, anc[6])
    qc.cx(q1, anc[6])
    qc.x(anc[6])
    qc.ccx(anc[6], anc[7], anc[8])
    
    qc.cx(q4, anc[4])
    qc.cx(q5, anc[4])
    
    qc.x(anc[3])
    qc.x(q2)
    qc.ccx(q2, q3, anc[3])
    qc.x(q2)
    
    qc.cx(q2, anc[2])
    qc.cx(q3, anc[2])
    
    qc.x(anc[1])
    qc.x(q0)
    qc.ccx(q0, q1, anc[1])
    qc.x(q0)
    
    qc.cx(q0, anc[0])
    qc.cx(q1, anc[0])
