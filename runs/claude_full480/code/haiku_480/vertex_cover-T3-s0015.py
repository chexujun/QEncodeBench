from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for vertex cover with k=3.
    Marks basis states where:
    1. All 9 edges are covered
    2. Population count <= 3
    """
    edges = [(0,1), (1,2), (1,3), (1,4), (2,4), (2,5), (3,4), (3,5), (4,5)]
    
    idx = 0
    
    # Ancillas for edge OR computations
    edge_or = [ancilla_qubits[i] for i in range(9)]
    idx = 9
    
    # Temporary ancilla for AND operations
    temp = ancilla_qubits[idx]
    idx += 1
    
    # Compute OR(x_i, x_j) for each edge, using formula: OR = XOR + AND
    for (i, j), anc in zip(edges, edge_or):
        xi, xj = problem_qubits[i], problem_qubits[j]
        qc.ccx(xi, xj, temp)
        qc.cx(xi, anc)
        qc.cx(xj, anc)
        qc.cx(temp, anc)
        qc.ccx(xi, xj, temp)
    
    # AND tree to combine all edge checks (Level 1: pair-wise ANDs)
    and_l1 = [ancilla_qubits[idx + i] for i in range(4)]
    idx += 4
    qc.ccx(edge_or[0], edge_or[1], and_l1[0])
    qc.ccx(edge_or[2], edge_or[3], and_l1[1])
    qc.ccx(edge_or[4], edge_or[5], and_l1[2])
    qc.ccx(edge_or[6], edge_or[7], and_l1[3])
    
    # Level 2: AND of Level 1 results
    and_l2_a = ancilla_qubits[idx]
    and_l2_b = ancilla_qubits[idx + 1]
    idx += 2
    qc.ccx(and_l1[0], and_l1[1], and_l2_a)
    qc.ccx(and_l1[2], and_l1[3], temp)
    qc.ccx(temp, edge_or[8], and_l2_b)
    
    # Level 3: Final AND for edge coverage
    edges_ok = ancilla_qubits[idx]
    idx += 1
    qc.ccx(and_l2_a, and_l2_b, edges_ok)
    
    # Compute popcount <= 3 using half-adders for (x0+x1), (x2+x3), (x4+x5)
    sum01 = ancilla_qubits[idx]
    carry01 = ancilla_qubits[idx + 1]
    idx += 2
    qc.cx(problem_qubits[0], sum01)
    qc.cx(problem_qubits[1], sum01)
    qc.ccx(problem_qubits[0], problem_qubits[1], carry01)
    
    sum23 = ancilla_qubits[idx]
    carry23 = ancilla_qubits[idx + 1]
    idx += 2
    qc.cx(problem_qubits[2], sum23)
    qc.cx(problem_qubits[3], sum23)
    qc.ccx(problem_qubits[2], problem_qubits[3], carry23)
    
    sum45 = ancilla_qubits[idx]
    carry45 = ancilla_qubits[idx + 1]
    idx += 2
    qc.cx(problem_qubits[4], sum45)
    qc.cx(problem_qubits[5], sum45)
    qc.ccx(problem_qubits[4], problem_qubits[5], carry45)
    
    # Check popcount <= 3: NOT(carry01 AND carry23 AND carry45)
    # Equivalently, pop_ok = 1 if NOT all three carries are 1
    pop_bad = ancilla_qubits[idx]
    idx += 1
    qc.ccx(carry01, carry23, temp)
    qc.ccx(temp, carry45, pop_bad)
    pop_ok = ancilla_qubits[idx]
    idx += 1
    qc.x(pop_bad)
    qc.cx(pop_bad, pop_ok)
    
    # Combine edge_ok AND pop_ok
    result = ancilla_qubits[idx]
    idx += 1
    qc.ccx(edges_ok, pop_ok, result)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute in reverse
    qc.ccx(edges_ok, pop_ok, result)
    qc.cx(pop_bad, pop_ok)
    qc.x(pop_bad)
    qc.ccx(temp, carry45, pop_bad)
    qc.ccx(carry01, carry23, temp)
    qc.ccx(problem_qubits[4], problem_qubits[5], carry45)
    qc.cx(problem_qubits[5], sum45)
    qc.cx(problem_qubits[4], sum45)
    qc.ccx(problem_qubits[2], problem_qubits[3], carry23)
    qc.cx(problem_qubits[3], sum23)
    qc.cx(problem_qubits[2], sum23)
    qc.ccx(problem_qubits[0], problem_qubits[1], carry01)
    qc.cx(problem_qubits[1], sum01)
    qc.cx(problem_qubits[0], sum01)
    qc.ccx(and_l2_a, and_l2_b, edges_ok)
    qc.ccx(temp, edge_or[8], and_l2_b)
    qc.ccx(and_l1[2], and_l1[3], temp)
    qc.ccx(and_l1[0], and_l1[1], and_l2_a)
    qc.ccx(edge_or[6], edge_or[7], and_l1[3])
    qc.ccx(edge_or[4], edge_or[5], and_l1[2])
    qc.ccx(edge_or[2], edge_or[3], and_l1[1])
    qc.ccx(edge_or[0], edge_or[1], and_l1[0])
    for (i, j), anc in zip(reversed(edges), reversed(edge_or)):
        xi, xj = problem_qubits[i], problem_qubits[j]
        qc.ccx(xi, xj, temp)
        qc.cx(temp, anc)
        qc.cx(xj, anc)
        qc.cx(xi, anc)
        qc.ccx(xi, xj, temp)
