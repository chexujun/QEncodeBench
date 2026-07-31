from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # Define the edges of the graph
    edges = [(0, 3), (1, 4), (2, 3), (3, 4)]
    
    # Step 1: Compute each constraint c_i = (b0_u XOR b0_v) XOR (b1_u XOR b1_v)
    # into ancilla_qubits[i]. This constraint is 1 iff vertices u and v have
    # different colors under the surjective decoding (00/11 -> 0, 01 -> 1, 10 -> 2).
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        # Compute: ancilla_qubits[i] ^= b0_u XOR b0_v XOR b1_u XOR b1_v
        qc.cx(b0_u, ancilla_qubits[i])
        qc.cx(b0_v, ancilla_qubits[i])
        qc.cx(b1_u, ancilla_qubits[i])
        qc.cx(b1_v, ancilla_qubits[i])
    
    # Step 2: Compute the AND of all constraints into ancilla_qubits[4]
    # Result: ancilla_qubits[4] = 1 iff all edges have endpoints with different colors
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], 
            ancilla_qubits[4])
    
    # Step 3: Apply phase -1 if all constraints are satisfied
    qc.z(ancilla_qubits[4])
    
    # Step 4: Uncompute the AND (restore ancilla_qubits[4] to |0>)
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], 
            ancilla_qubits[4])
    
    # Step 5: Uncompute each constraint (restore ancilla_qubits[i] to |0>)
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        qc.cx(b1_v, ancilla_qubits[i])
        qc.cx(b1_u, ancilla_qubits[i])
        qc.cx(b0_v, ancilla_qubits[i])
        qc.cx(b0_u, ancilla_qubits[i])
