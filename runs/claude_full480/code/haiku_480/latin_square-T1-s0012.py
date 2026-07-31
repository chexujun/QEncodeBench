from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits[0:4]
    a0, a1, a2, a3 = ancilla_qubits[0:4]
    
    # === COMPUTE ===
    # a0 = q0 XOR q1
    qc.cx(q0, a0)
    qc.cx(q1, a0)
    
    # a1 = NOT q2 (i.e., 1 iff q2 == 0)
    qc.x(q2)
    qc.cx(q2, a1)
    qc.x(q2)
    
    # a2 = q3
    qc.cx(q3, a2)
    
    # === PHASE ===
    # Flip a0 to prepare control (now a0 = NOT (q0 XOR q1) = q0 XNOR q1)
    qc.x(a0)
    
    # Compute a3 = a0 AND a1 AND a2 (which is 1 when all constraints are satisfied)
    qc.mcx([a0, a1, a2], a3)
    
    # Apply phase -1 if a3 == 1
    qc.z(a3)
    
    # Uncompute a3
    qc.mcx([a0, a1, a2], a3)
    
    # Restore a0
    qc.x(a0)
    
    # === UNCOMPUTE ===
    # Reverse the compute steps
    qc.cx(q3, a2)
    
    qc.x(q2)
    qc.cx(q2, a1)
    qc.x(q2)
    
    qc.cx(q1, a0)
    qc.cx(q0, a0)
