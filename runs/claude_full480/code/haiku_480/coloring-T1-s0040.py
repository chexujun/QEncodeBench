from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 2), (1, 3), (2, 3)]
    result_anc = ancilla_qubits[4]
    
    # Initialize result_anc = 1 (will accumulate AND of all edge validities)
    qc.x(result_anc)
    
    # For each edge, compute whether colors differ and AND into result_anc
    for u, v in edges:
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        xor0_anc = ancilla_qubits[0]
        xor1_anc = ancilla_qubits[1]
        temp_anc = ancilla_qubits[2]
        
        # Compute b0_u XOR b0_v and b1_u XOR b1_v into ancillas
        qc.cx(b0_u, xor0_anc)
        qc.cx(b0_v, xor0_anc)
        qc.cx(b1_u, xor1_anc)
        qc.cx(b1_v, xor1_anc)
        
        # Compute edge_valid = (b0_u XOR b0_v) OR (b1_u XOR b1_v)
        # Using identity: a OR b = NOT((NOT a) AND (NOT b))
        qc.x(xor0_anc)
        qc.x(xor1_anc)
        qc.ccx(xor0_anc, xor1_anc, temp_anc)
        qc.x(temp_anc)  # temp_anc now holds edge_valid
        
        # Apply AND: result_anc := result_anc AND edge_valid
        # Flip to NOT(edge_valid) for the AND gate logic
        qc.x(temp_anc)
        qc.ccx(temp_anc, result_anc, result_anc)
        qc.x(temp_anc)
        
        # Uncompute ancillas (restore to |0>)
        qc.x(temp_anc)
        qc.ccx(xor0_anc, xor1_anc, temp_anc)
        qc.x(xor1_anc)
        qc.x(xor0_anc)
        qc.cx(b1_v, xor1_anc)
        qc.cx(b1_u, xor1_anc)
        qc.cx(b0_v, xor0_anc)
        qc.cx(b0_u, xor0_anc)
    
    # Apply Z phase (flips sign if result_anc = 1, i.e., all constraints satisfied)
    qc.z(result_anc)
    
    # Uncompute: reverse all edges in reverse order to restore ancillas
    for u, v in reversed(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        xor0_anc = ancilla_qubits[0]
        xor1_anc = ancilla_qubits[1]
        temp_anc = ancilla_qubits[2]
        
        qc.cx(b0_u, xor0_anc)
        qc.cx(b0_v, xor0_anc)
        qc.cx(b1_u, xor1_anc)
        qc.cx(b1_v, xor1_anc)
        
        qc.x(xor0_anc)
        qc.x(xor1_anc)
        qc.ccx(xor0_anc, xor1_anc, temp_anc)
        qc.x(temp_anc)
        
        qc.x(temp_anc)
        qc.ccx(temp_anc, result_anc, result_anc)
        qc.x(temp_anc)
    
    # Restore result_anc to |0>
    qc.x(result_anc)
