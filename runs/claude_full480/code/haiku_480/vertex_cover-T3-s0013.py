from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [
        (0,1), (0,2), (0,4), (0,5),
        (1,4), (1,5),
        (2,4), (2,5),
        (3,4), (3,5)
    ]
    
    # Compute coverage for each edge (x_u OR x_v)
    for i, (u, v) in enumerate(edges):
        a = ancilla_qubits[i]
        qc.cx(problem_qubits[u], a)
        qc.cx(problem_qubits[v], a)
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
    
    # Compute AND of all edge coverages
    qc.mcx([ancilla_qubits[i] for i in range(10)], ancilla_qubits[10])
    
    # Uncompute edge coverage
    for i in range(9, -1, -1):
        u, v = edges[i]
        a = ancilla_qubits[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.cx(problem_qubits[v], a)
        qc.cx(problem_qubits[u], a)
    
    # Compute popcount in ancillas 0-2 (3-bit number)
    for x_idx in range(6):
        x = problem_qubits[x_idx]
        c0 = ancilla_qubits[0]
        c1 = ancilla_qubits[1]
        c2 = ancilla_qubits[2]
        carry = ancilla_qubits[11]
        carry2 = ancilla_qubits[12]
        
        # Add x to 3-bit counter
        qc.ccx(x, c0, carry)
        qc.cx(x, c0)
        qc.ccx(carry, c1, carry2)
        qc.cx(carry, c1)
        qc.ccx(carry2, c2, carry)
        qc.cx(carry2, c2)
        qc.cx(carry, c1)
        qc.ccx(carry, c1, carry2)
        qc.cx(carry2, c2)
        qc.ccx(carry2, c2, carry)
    
    # Check popcount < 4: true iff c2 == 0
    popcount_ok = ancilla_qubits[3]
    qc.x(popcount_ok)
    qc.cx(ancilla_qubits[2], popcount_ok)
    
    # Compute result = all_covered AND popcount_ok
    result = ancilla_qubits[4]
    qc.ccx(ancilla_qubits[10], popcount_ok, result)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute result
    qc.ccx(ancilla_qubits[10], popcount_ok, result)
    
    # Uncompute popcount_ok
    qc.cx(ancilla_qubits[2], popcount_ok)
    qc.x(popcount_ok)
    
    # Uncompute popcount (reverse the additions)
    for x_idx in range(5, -1, -1):
        x = problem_qubits[x_idx]
        c0 = ancilla_qubits[0]
        c1 = ancilla_qubits[1]
        c2 = ancilla_qubits[2]
        carry = ancilla_qubits[11]
        carry2 = ancilla_qubits[12]
        
        qc.ccx(carry2, c2, carry)
        qc.cx(carry2, c2)
        qc.ccx(carry, c1, carry2)
        qc.cx(carry, c1)
        qc.ccx(x, c0, carry)
        qc.cx(x, c0)
    
    # Uncompute all_covered
    qc.mcx([ancilla_qubits[i] for i in range(10)], ancilla_qubits[10])
