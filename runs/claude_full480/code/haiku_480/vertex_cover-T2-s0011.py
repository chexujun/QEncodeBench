from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for vertex cover <= 3: f(x) = 1 iff x is a vertex cover of size <= 3.
    Applies phase -1 to marked states.
    """
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 4)]
    
    edge_ancillas = ancilla_qubits[0:6]
    all_covered_ancilla = ancilla_qubits[6]
    size_ok_ancilla = ancilla_qubits[7]
    final_result_ancilla = ancilla_qubits[8]
    
    # Compute coverage for each edge (OR of endpoints)
    for idx, (i, j) in enumerate(edges):
        a = edge_ancillas[idx]
        qc.cx(problem_qubits[i], a)
        qc.cx(problem_qubits[j], a)
        qc.mcx([problem_qubits[i], problem_qubits[j]], a)
    
    # Compute all_edges_covered = AND of all coverages
    qc.mcx(edge_ancillas, all_covered_ancilla)
    
    # Uncompute edge coverages to free space
    for idx, (i, j) in enumerate(edges):
        a = edge_ancillas[idx]
        qc.mcx([problem_qubits[i], problem_qubits[j]], a)
        qc.cx(problem_qubits[j], a)
        qc.cx(problem_qubits[i], a)
    
    # Compute size_ok = (count <= 3) = NOT(all_ones OR exactly_one_zero)
    all_ones_ancilla = ancilla_qubits[0]
    exactly_one_zero_ancilla = ancilla_qubits[1]
    temp_term_ancilla = ancilla_qubits[2]
    
    # Compute all_ones
    qc.mcx(problem_qubits, all_ones_ancilla)
    
    # Compute exactly_one_zero (OR of "x[i]=0 and all others=1" for each i)
    for zero_idx in range(5):
        qc.x(problem_qubits[zero_idx])
        qc.mcx(problem_qubits, temp_term_ancilla)
        qc.x(problem_qubits[zero_idx])
        qc.cx(temp_term_ancilla, exactly_one_zero_ancilla)
        qc.x(problem_qubits[zero_idx])
        qc.mcx(problem_qubits, temp_term_ancilla)
        qc.x(problem_qubits[zero_idx])
    
    # Compute size_ok = 1 XOR all_ones XOR exactly_one_zero
    qc.x(size_ok_ancilla)
    qc.cx(all_ones_ancilla, size_ok_ancilla)
    qc.cx(exactly_one_zero_ancilla, size_ok_ancilla)
    
    # Compute final result = all_edges_covered AND size_ok
    qc.mcx([all_covered_ancilla, size_ok_ancilla], final_result_ancilla)
    
    # Apply phase -1
    qc.z(final_result_ancilla)
    
    # Uncompute (reverse order)
    qc.mcx([all_covered_ancilla, size_ok_ancilla], final_result_ancilla)
    
    qc.cx(exactly_one_zero_ancilla, size_ok_ancilla)
    qc.cx(all_ones_ancilla, size_ok_ancilla)
    qc.x(size_ok_ancilla)
    
    for zero_idx in range(4, -1, -1):
        qc.x(problem_qubits[zero_idx])
        qc.mcx(problem_qubits, temp_term_ancilla)
        qc.x(problem_qubits[zero_idx])
        qc.cx(temp_term_ancilla, exactly_one_zero_ancilla)
        qc.x(problem_qubits[zero_idx])
        qc.mcx(problem_qubits, temp_term_ancilla)
        qc.x(problem_qubits[zero_idx])
    
    qc.mcx(problem_qubits, all_ones_ancilla)
    
    # Recompute edge coverages for uncomputing all_covered
    for idx, (i, j) in enumerate(edges):
        a = edge_ancillas[idx]
        qc.cx(problem_qubits[i], a)
        qc.cx(problem_qubits[j], a)
        qc.mcx([problem_qubits[i], problem_qubits[j]], a)
    
    qc.mcx(edge_ancillas, all_covered_ancilla)
    
    # Uncompute edge coverages
    for idx, (i, j) in enumerate(edges):
        a = edge_ancillas[idx]
        qc.mcx([problem_qubits[i], problem_qubits[j]], a)
        qc.cx(problem_qubits[j], a)
        qc.cx(problem_qubits[i], a)
