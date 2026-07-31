from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 4), (2, 3)]
    
    # Step 1: Compute colors_equal for each edge into ancilla[0..3]
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        result_anc = ancilla_qubits[i]
        
        # Colors are equal for these (b0_u, b1_u, b0_v, b1_v) patterns:
        # (0,0,0,0), (0,0,1,1), (0,1,0,1), (1,0,1,0), (1,1,0,0), (1,1,1,1)
        
        # Case 1: (0,0,0,0)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Case 2: (0,0,1,1)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_u)
        qc.x(b1_u)
        
        # Case 3: (0,1,0,1)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_u)
        qc.x(b0_v)
        
        # Case 4: (1,0,1,0)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b1_u)
        qc.x(b1_v)
        
        # Case 5: (1,1,0,0)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Case 6: (1,1,1,1)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
    
    # Step 2: Compute temp_anc = NOT(any_equal) using all-control AND
    temp_anc = ancilla_qubits[4]
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[2])
    qc.x(ancilla_qubits[3])
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], temp_anc)
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[2])
    qc.x(ancilla_qubits[3])
    
    # Step 3: Apply phase -1 iff all edges satisfied (temp_anc=1)
    qc.z(temp_anc)
    
    # Step 4: Uncompute temp_anc
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[2])
    qc.x(ancilla_qubits[3])
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], temp_anc)
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[2])
    qc.x(ancilla_qubits[3])
    
    # Step 5: Uncompute colors_equal for each edge (reverse order)
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        result_anc = ancilla_qubits[i]
        
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], result_anc)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
