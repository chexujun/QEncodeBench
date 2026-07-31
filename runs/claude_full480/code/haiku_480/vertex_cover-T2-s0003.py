from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 4), (2, 4), (3, 4)]
    
    validity = ancilla_qubits[0]
    temp1 = ancilla_qubits[1]
    temp2 = ancilla_qubits[2]
    temp_pc = ancilla_qubits[3]
    
    # ==== COMPUTE EDGE COVERAGE ====
    qc.x(validity)  # Start with validity = 1
    
    # For each edge (u,v), flip validity if edge is NOT covered (both endpoints absent)
    for u, v in edges:
        qc.cx(problem_qubits[u], temp1)
        qc.x(temp1)  # temp1 = NOT x[u]
        qc.cx(problem_qubits[v], temp2)
        qc.x(temp2)  # temp2 = NOT x[v]
        qc.ccx(temp1, temp2, validity)  # Flip if both endpoints absent
        # Uncompute within loop
        qc.x(temp2)
        qc.cx(problem_qubits[v], temp2)
        qc.x(temp1)
        qc.cx(problem_qubits[u], temp1)
    
    # ==== COMPUTE POPCOUNT > 3 CONDITION ====
    # Flip validity if popcount >= 4
    # This happens when all 5 qubits are 1 OR exactly 4 are 1
    qc.mcx(problem_qubits, validity)  # All 5 ones case
    
    # Exactly 4 ones case (one qubit is 0)
    for missing_idx in range(5):
        controls = [problem_qubits[i] for i in range(5) if i != missing_idx]
        not_missing_qubit = problem_qubits[missing_idx]
        
        qc.cx(not_missing_qubit, temp_pc)
        qc.x(temp_pc)  # temp_pc = NOT x[missing_idx]
        qc.mcx(controls + [temp_pc], validity)
        qc.x(temp_pc)
        qc.cx(not_missing_qubit, temp_pc)
    
    # ==== APPLY PHASE ====
    qc.z(validity)
    
    # ==== UNCOMPUTE POPCOUNT ====
    for missing_idx in range(4, -1, -1):
        controls = [problem_qubits[i] for i in range(5) if i != missing_idx]
        not_missing_qubit = problem_qubits[missing_idx]
        
        qc.cx(not_missing_qubit, temp_pc)
        qc.x(temp_pc)
        qc.mcx(controls + [temp_pc], validity)
        qc.x(temp_pc)
        qc.cx(not_missing_qubit, temp_pc)
    
    qc.mcx(problem_qubits, validity)
    
    # ==== UNCOMPUTE EDGE COVERAGE ====
    for u, v in reversed(edges):
        qc.cx(problem_qubits[u], temp1)
        qc.x(temp1)
        qc.cx(problem_qubits[v], temp2)
        qc.x(temp2)
        qc.ccx(temp1, temp2, validity)
        qc.x(temp2)
        qc.cx(problem_qubits[v], temp2)
        qc.x(temp1)
        qc.cx(problem_qubits[u], temp1)
    
    qc.x(validity)
