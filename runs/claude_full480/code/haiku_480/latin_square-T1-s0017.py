from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    a0, a1, a2 = ancilla_qubits[:3]
    
    # Constraints for valid Latin square completion:
    # 1. Cell 0 (row 2, col 0) must be 2: encoded as q0=0, q1=1
    # 2. Cell 1 (row 2, col 2) must be 0: encoded as q2==q3
    # Both columns 0 and 1 are already satisfied.
    
    # Step 1: Flip q0 to condition on q0=0 in original state
    qc.x(q0)
    
    # Step 2: Compute q2 XOR q3 into a1
    qc.cx(q2, a1)
    qc.cx(q3, a1)
    
    # Step 3: Flip a1 to get NOT(q2 XOR q3) = (q2 == q3)
    qc.x(a1)
    
    # Step 4: Compute (flipped_q0 AND q1) into a0
    qc.ccx(q0, q1, a0)
    
    # Step 5: Compute (a0 AND a1) into a2
    qc.ccx(a0, a1, a2)
    
    # Step 6: Apply phase -1 when all conditions met
    qc.z(a2)
    
    # Step 7: Uncompute in reverse order
    qc.ccx(a0, a1, a2)
    qc.ccx(q0, q1, a0)
    
    # Step 8: Uncompute a1
    qc.x(a1)
    qc.cx(q3, a1)
    qc.cx(q2, a1)
    
    # Step 9: Flip q0 back
    qc.x(q0)
