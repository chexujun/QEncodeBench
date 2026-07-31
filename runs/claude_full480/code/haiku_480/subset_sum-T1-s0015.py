def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    a0, a1 = ancilla_qubits[0], ancilla_qubits[1]
    
    # Predicate: f(x) = 1 iff sum of selected elements equals 8
    # For a = [6, 6, 2], this happens when:
    #   - a[0] + a[2] = 6 + 2 = 8  (x = 101, i.e., x0=1, x1=0, x2=1)
    #   - a[1] + a[2] = 6 + 2 = 8  (x = 110, i.e., x0=0, x1=1, x2=1)
    # Simplified condition: f(x) = x2 AND (x0 XOR x1)
    
    # Compute x0 XOR x1 into a0
    qc.cx(x0, a0)
    qc.cx(x1, a0)
    
    # Compute (x0 XOR x1) AND x2 into a1 using Toffoli
    qc.ccx(a0, x2, a1)
    
    # Apply phase -1 to marked states
    qc.z(a1)
    
    # Uncompute: restore ancillas to |0>
    qc.ccx(a0, x2, a1)
    qc.cx(x1, a0)
    qc.cx(x0, a0)
