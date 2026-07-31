from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]
    
    # Initialize predicate ancilla to |1>
    qc.x(ancilla_qubits[0])
    
    # Compute: for each edge, if colors are the same, flip the predicate
    for u, v in edges:
        u_b0 = problem_qubits[2 * u]
        u_b1 = problem_qubits[2 * u + 1]
        v_b0 = problem_qubits[2 * v]
        v_b1 = problem_qubits[2 * v + 1]
        
        temp = ancilla_qubits[1]
        
        # Compute: temp = u_b0 XOR v_b0 XOR u_b1 XOR v_b1
        # (1 if colors differ, 0 if colors same)
        qc.cx(u_b0, temp)
        qc.cx(v_b0, temp)
        qc.cx(u_b1, temp)
        qc.cx(v_b1, temp)
        
        # If colors are the same, flip the predicate
        qc.x(temp)
        qc.cx(temp, ancilla_qubits[0])
        qc.x(temp)
        
        # Uncompute: restore temp to |0>
        qc.cx(v_b1, temp)
        qc.cx(u_b1, temp)
        qc.cx(v_b0, temp)
        qc.cx(u_b0, temp)
    
    # Phase: apply Z to the predicate ancilla
    qc.z(ancilla_qubits[0])
    
    # Uncompute: reverse the compute phase
    for u, v in reversed(edges):
        u_b0 = problem_qubits[2 * u]
        u_b1 = problem_qubits[2 * u + 1]
        v_b0 = problem_qubits[2 * v]
        v_b1 = problem_qubits[2 * v + 1]
        
        temp = ancilla_qubits[1]
        
        # Compute: temp = u_b0 XOR v_b0 XOR u_b1 XOR v_b1
        qc.cx(u_b0, temp)
        qc.cx(v_b0, temp)
        qc.cx(u_b1, temp)
        qc.cx(v_b1, temp)
        
        # If colors are the same, flip the predicate
        qc.x(temp)
        qc.cx(temp, ancilla_qubits[0])
        qc.x(temp)
        
        # Uncompute: restore temp to |0>
        qc.cx(v_b1, temp)
        qc.cx(u_b1, temp)
        qc.cx(v_b0, temp)
        qc.cx(u_b0, temp)
    
    # Undo the initialization
    qc.x(ancilla_qubits[0])
