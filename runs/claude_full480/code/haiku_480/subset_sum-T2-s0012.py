def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for subset sum: mark states where sum equals 20.
    Elements: a = [4, 10, 5, 6]
    Target: T = 20
    Only solution: select indices {0, 1, 3} → {4, 10, 6} = 20
    Marked state: x_0 AND x_1 AND NOT(x_2) AND x_3
    """
    
    # Assign ancillas for cascading AND operations
    and_1 = ancilla_qubits[0]    # x_0 AND x_1
    and_2 = ancilla_qubits[1]    # and_1 AND NOT(x_2)
    mark = ancilla_qubits[2]     # and_2 AND x_3 (result qubit for phase)
    
    # COMPUTE PHASE: Build the marking predicate
    # Flip x_2 so we can check NOT(x_2) via AND with the flipped bit
    qc.x(problem_qubits[2])
    
    # Compute x_0 AND x_1 → and_1
    qc.ccx(problem_qubits[0], problem_qubits[1], and_1)
    
    # Compute and_1 AND NOT(x_2) → and_2
    # (x_2 is now flipped, so this is and_1 AND flipped_x_2)
    qc.ccx(and_1, problem_qubits[2], and_2)
    
    # Compute and_2 AND x_3 → mark
    qc.ccx(and_2, problem_qubits[3], mark)
    
    # APPLY PHASE: Z gate applies phase -1 when mark=1 (i.e., for target state)
    qc.z(mark)
    
    # UNCOMPUTE: Restore all ancillas to |0⟩ by reversing compute steps
    qc.ccx(and_2, problem_qubits[3], mark)
    qc.ccx(and_1, problem_qubits[2], and_2)
    qc.ccx(problem_qubits[0], problem_qubits[1], and_1)
    
    # Flip x_2 back to original state
    qc.x(problem_qubits[2])
