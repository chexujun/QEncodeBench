from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubit indices for the three free cells
    q0, q1 = problem_qubits[0], problem_qubits[1]  # Free cell 0 at (1,1)
    q2, q3 = problem_qubits[2], problem_qubits[3]  # Free cell 1 at (2,0)
    q4, q5 = problem_qubits[4], problem_qubits[5]  # Free cell 2 at (2,2)
    
    # Ancilla qubits for storing intermediate results
    a0 = ancilla_qubits[0]  # c0 = q0 AND NOT q1
    a1 = ancilla_qubits[1]  # c1 = NOT q2 AND q3
    a2 = ancilla_qubits[2]  # c2 = q4 AND NOT q5
    a3 = ancilla_qubits[3]  # a0 AND a1
    a4 = ancilla_qubits[4]  # a3 AND a2 (final flag)
    
    # Compute: c0 = q0 AND NOT q1
    qc.x(q1)
    qc.ccx(q0, q1, a0)
    qc.x(q1)
    
    # Compute: c1 = NOT q2 AND q3
    qc.x(q2)
    qc.ccx(q2, q3, a1)
    qc.x(q2)
    
    # Compute: c2 = q4 AND NOT q5
    qc.x(q5)
    qc.ccx(q4, q5, a2)
    qc.x(q5)
    
    # Combine: a3 = a0 AND a1
    qc.ccx(a0, a1, a3)
    
    # Combine: a4 = a3 AND a2 (all conditions satisfied)
    qc.ccx(a3, a2, a4)
    
    # Apply phase -1
    qc.z(a4)
    
    # Uncompute in reverse order
    qc.ccx(a3, a2, a4)
    qc.ccx(a0, a1, a3)
    
    # Uncompute: c2
    qc.x(q5)
    qc.ccx(q4, q5, a2)
    qc.x(q5)
    
    # Uncompute: c1
    qc.x(q2)
    qc.ccx(q2, q3, a1)
    qc.x(q2)
    
    # Uncompute: c0
    qc.x(q1)
    qc.ccx(q0, q1, a0)
    qc.x(q1)
