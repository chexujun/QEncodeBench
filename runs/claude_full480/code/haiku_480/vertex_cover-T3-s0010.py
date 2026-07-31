from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [
        (0, 1), (0, 2), (0, 3), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
        (3, 5), (4, 5)
    ]
    
    # Ancilla allocation:
    # ancilla_qubits[0:10] for edge coverage flags
    # ancilla_qubits[10] for popcount check flag
    # ancilla_qubits[11:13] for workspace
    
    edge_flags = ancilla_qubits[0:10]
    edge_valid_flag = ancilla_qubits[10]
    popcount_invalid_flag = ancilla_qubits[11]
    workspace = ancilla_qubits[12]
    
    # Compute: for each edge (i,j), edge_flags[idx] = 1 iff edge is covered (q[i] OR q[j])
    for idx, (i, j) in enumerate(edges):
        qi, qj = problem_qubits[i], problem_qubits[j]
        flag = edge_flags[idx]
        
        # Compute flag = q[i] OR q[j]
        # flag = q[i] + q[j] - q[i]*q[j], which is q[i] XOR q[j] XOR (q[i] AND q[j])
        qc.cx(qi, flag)  # flag = q[i]
        qc.ccx(qi, qj, workspace)  # workspace = q[i] AND q[j]
        qc.cx(qj, flag)  # flag = q[i] XOR q[j]
        qc.cx(workspace, flag)  # flag = q[i] XOR q[j] XOR workspace = q[i] OR q[j]
        qc.ccx(qi, qj, workspace)  # uncompute workspace
    
    # Check all edges are covered: edge_valid_flag = AND(all edge_flags)
    qc.mcx(edge_flags, edge_valid_flag)
    
    # Check popcount <= 4: popcount >= 5 is invalid
    # Build list of all 5-element subsets of problem qubits
    # If any 5-element subset is all 1s, popcount >= 5
    five_subsets = [
        [0, 1, 2, 3, 4], [0, 1, 2, 3, 5], [0, 1, 2, 4, 5],
        [0, 1, 3, 4, 5], [0, 2, 3, 4, 5], [1, 2, 3, 4, 5]
    ]
    
    for subset in five_subsets:
        qc.mcx([problem_qubits[i] for i in subset], workspace)
        qc.cx(workspace, popcount_invalid_flag)
        qc.mcx([problem_qubits[i] for i in subset], workspace)
    
    # Apply phase if both conditions hold
    # valid = edge_valid_flag AND NOT(popcount_invalid_flag)
    qc.x(popcount_invalid_flag)  # Flip to get NOT
    qc.ccx(edge_valid_flag, popcount_invalid_flag, workspace)  # workspace = both valid
    qc.z(workspace)  # Apply phase
    qc.ccx(edge_valid_flag, popcount_invalid_flag, workspace)  # uncompute
    qc.x(popcount_invalid_flag)  # Flip back
    
    # Uncompute popcount check
    for subset in five_subsets:
        qc.mcx([problem_qubits[i] for i in subset], workspace)
        qc.cx(workspace, popcount_invalid_flag)
        qc.mcx([problem_qubits[i] for i in subset], workspace)
    
    # Uncompute edge coverage flags
    for idx, (i, j) in enumerate(edges):
        qi, qj = problem_qubits[i], problem_qubits[j]
        flag = edge_flags[idx]
        qc.ccx(qi, qj, workspace)  # workspace = q[i] AND q[j]
        qc.cx(workspace, flag)  # undo q[i] XOR q[j] XOR workspace
        qc.cx(qj, flag)  # undo q[i] XOR q[j]
        qc.ccx(qi, qj, workspace)  # uncompute workspace
        qc.cx(qi, flag)  # undo q[i]
    
    # Uncompute edge_valid_flag
    qc.mcx(edge_flags, edge_valid_flag)
