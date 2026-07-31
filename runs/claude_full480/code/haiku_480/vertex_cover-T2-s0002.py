from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # Graph edges
    edges = [(0, 1), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4)]
    # All pairs of problem qubits for popcount check
    pairs = [(i, j) for i in range(5) for j in range(i+1, 5)]
    
    # Allocate ancillas
    result = ancilla_qubits[0]           # 1 if f(x)=1, else 0
    edge_temp = ancilla_qubits[1]        # Temporary for OR computation
    pair_temp = ancilla_qubits[2]        # Temporary for (NOT x_i AND NOT x_j)
    at_least_2_zeros = ancilla_qubits[3] # 1 if popcount <= 3
    
    # FORWARD: Initialize result to 1
    qc.x(result)
    
    # FORWARD: Compute result AND (all edges covered)
    for i, j in edges:
        # Compute x_i OR x_j into edge_temp
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], edge_temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
        qc.x(edge_temp)  # Convert NOT(both_zero) to OR
        
        # AND: result &= edge_temp using a ^= a AND NOT b
        qc.x(edge_temp)
        qc.ccx(result, edge_temp, result)
        qc.x(edge_temp)
    
    # FORWARD: Detect at least 2 zeros (popcount <= 3)
    for i, j in pairs:
        # Compute (NOT x_i) AND (NOT x_j) into pair_temp
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], pair_temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
        
        # OR into at_least_2_zeros
        qc.cx(pair_temp, at_least_2_zeros)
    
    # FORWARD: AND result with (NOT at_least_2_zeros)
    qc.x(at_least_2_zeros)
    qc.ccx(result, at_least_2_zeros, result)
    qc.x(at_least_2_zeros)
    
    # Phase
    qc.z(result)
    
    # BACKWARD: Undo AND
    qc.x(at_least_2_zeros)
    qc.ccx(result, at_least_2_zeros, result)
    qc.x(at_least_2_zeros)
    
    # BACKWARD: Uncompute at_least_2_zeros
    for i, j in reversed(pairs):
        qc.cx(pair_temp, at_least_2_zeros)
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], pair_temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
    
    # BACKWARD: Uncompute edges
    for i, j in reversed(edges):
        qc.x(edge_temp)
        qc.ccx(result, edge_temp, result)
        qc.x(edge_temp)
        qc.x(edge_temp)
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], edge_temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
    
    # BACKWARD: Uncompute result
    qc.x(result)
