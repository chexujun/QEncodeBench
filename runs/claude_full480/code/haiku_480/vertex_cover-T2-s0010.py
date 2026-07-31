from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 4), (3, 4)]
    triples = [(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4), (0, 3, 4),
               (1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)]
    
    e = ancilla_qubits[0:6]
    f_e = ancilla_qubits[6]
    f_s = ancilla_qubits[7]
    temp = ancilla_qubits[8]
    
    # === COMPUTE ===
    
    # Compute edge coverage: e[i] = problem_qubits[u] OR problem_qubits[v]
    for i, (u, v) in enumerate(edges):
        qc.cx(problem_qubits[u], e[i])
        qc.cx(problem_qubits[v], e[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], e[i])
    
    # Compute f_e = AND of all edge coverage bits
    qc.mcx(e, f_e)
    
    # Compute f_s = 1 iff size <= 2 (i.e., NOT(any triple is all 1s))
    qc.x(f_s)
    for (i, j, k) in triples:
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.ccx(temp, problem_qubits[k], temp)
        qc.cx(temp, f_s)
        qc.ccx(temp, problem_qubits[k], temp)
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
    
    # Compute phase bit: temp = f_e AND f_s
    qc.ccx(f_e, f_s, temp)
    
    # Apply phase
    qc.z(temp)
    
    # === UNCOMPUTE ===
    
    # Uncompute phase bit
    qc.ccx(f_e, f_s, temp)
    
    # Uncompute f_s
    for (i, j, k) in triples:
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.ccx(temp, problem_qubits[k], temp)
        qc.cx(temp, f_s)
        qc.ccx(temp, problem_qubits[k], temp)
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
    qc.x(f_s)
    
    # Uncompute f_e
    qc.mcx(e, f_e)
    
    # Uncompute edge coverage
    for i, (u, v) in enumerate(edges):
        qc.ccx(problem_qubits[u], problem_qubits[v], e[i])
        qc.cx(problem_qubits[v], e[i])
        qc.cx(problem_qubits[u], e[i])
