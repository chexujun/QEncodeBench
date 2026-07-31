from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2 = problem_qubits
    a0, a1 = ancilla_qubits[0], ancilla_qubits[1]
    
    # Oracle for subset sum: mark states where sum equals 6
    # Condition: (q0 XOR q1) AND q2
    # (This captures both solutions: (1,0,1) and (0,1,1))
    
    # Compute q0 XOR q1 into a0
    qc.cx(q0, a0)
    qc.cx(q1, a0)
    
    # Compute a0 AND q2 into a1
    qc.ccx(a0, q2, a1)
    
    # Apply phase flip to a1
    qc.z(a1)
    
    # Uncompute a1
    qc.ccx(a0, q2, a1)
    
    # Uncompute a0
    qc.cx(q1, a0)
    qc.cx(q0, a0)
