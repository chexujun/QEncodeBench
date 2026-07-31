from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for each free cell
    q0, q1 = problem_qubits[0], problem_qubits[1]  # Free cell (1,1)
    q2, q3 = problem_qubits[2], problem_qubits[3]  # Free cell (1,2)
    q4, q5 = problem_qubits[4], problem_qubits[5]  # Free cell (2,2)
    
    # Extract ancilla qubits
    a0 = ancilla_qubits[0]      # Condition: q0 == q1 (free cell 0 = 0)
    a1 = ancilla_qubits[1]      # Condition: q2 = 0 AND q3 = 1 (free cell 1 = 2)
    a2 = ancilla_qubits[2]      # Condition: q4 = 1 AND q5 = 0 (free cell 2 = 1)
    a_temp = ancilla_qubits[3]  # Temporary for AND chain
    a_flag = ancilla_qubits[4]  # Final result for phase kickback
    
    # Condition 1: Free cell 0 must be value 0
    # Value 0 iff (q0, q1) in {(0,0), (1,1)}, i.e., q0 == q1
    qc.cx(q0, a0)      # a0 = q0 XOR q1
    qc.cx(q1, a0)
    qc.x(a0)           # a0 = NOT(q0 XOR q1) = (q0 == q1)
    
    # Condition 2: Free cell 1 must be value 2
    # Value 2 iff (q2, q3) = (0, 1), i.e., q2 = 0 AND q3 = 1
    qc.x(q2)           # Flip q2 to get NOT q2
    qc.ccx(q2, q3, a1) # a1 = (NOT q2) AND q3
    qc.x(q2)           # Flip q2 back
    
    # Condition 3: Free cell 2 must be value 1
    # Value 1 iff (q4, q5) = (1, 0), i.e., q4 = 1 AND q5 = 0
    qc.x(q5)           # Flip q5 to get NOT q5
    qc.ccx(q4, q5, a2) # a2 = q4 AND (NOT q5)
    qc.x(q5)           # Flip q5 back
    
    # Combine all conditions: a_flag = a0 AND a1 AND a2
    qc.ccx(a0, a1, a_temp)      # a_temp = a0 AND a1
    qc.ccx(a_temp, a2, a_flag)  # a_flag = a_temp AND a2
    
    # Apply phase -1 if all conditions are satisfied
    qc.z(a_flag)
    
    # Uncompute: reverse all operations to restore ancillas to |0>
    qc.ccx(a_temp, a2, a_flag)
    qc.ccx(a0, a1, a_temp)
    
    qc.x(q5)
    qc.ccx(q4, q5, a2)
    qc.x(q5)
    
    qc.x(q2)
    qc.ccx(q2, q3, a1)
    qc.x(q2)
    
    qc.x(a0)
    qc.cx(q1, a0)
    qc.cx(q0, a0)
