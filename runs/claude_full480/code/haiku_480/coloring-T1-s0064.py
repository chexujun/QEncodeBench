from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Vertices: 0,1,2,3 with 2-bit codes on problem_qubits[0:2], [2:4], [4:6], [6:8]
    # Edges: (0,1), (0,3), (1,3), (2,3)
    # f(x) = 1 iff all edges connect vertices with different colors
    
    edges = [(0, 1), (0, 3), (1, 3), (2, 3)]
    
    # Step 1: Compute color-match for each edge into ancilla[0:4]
    # Two vertices match colors (bad) for exactly 6 out of 16 code combinations:
    # (0,0,0,0), (0,0,1,1), (0,1,0,1), (1,0,1,0), (1,1,0,0), (1,1,1,1)
    # These patterns are mutually exclusive, so 6 mcx gates with XOR semantics = OR
    for idx, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='0000')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='0011')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='0101')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='1010')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='1100')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='1111')
    
    # Step 2: Flip match bits to NOT match
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Step 3: AND all NOT-match bits using Toffoli chain
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[4])
    qc.ccx(ancilla_qubits[2], ancilla_qubits[4], ancilla_qubits[0])
    qc.ccx(ancilla_qubits[3], ancilla_qubits[0], ancilla_qubits[4])
    qc.ccx(ancilla_qubits[2], ancilla_qubits[4], ancilla_qubits[0])
    
    # Step 4: Apply phase (-1) if f(x) = 1 (all edges differ)
    qc.z(ancilla_qubits[4])
    
    # Step 5: Uncompute AND chain
    qc.ccx(ancilla_qubits[2], ancilla_qubits[4], ancilla_qubits[0])
    qc.ccx(ancilla_qubits[3], ancilla_qubits[0], ancilla_qubits[4])
    qc.ccx(ancilla_qubits[2], ancilla_qubits[4], ancilla_qubits[0])
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[4])
    
    # Step 6: Flip match bits back
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Step 7: Uncompute match (mirror of compute)
    for idx, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='1111')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='1100')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='1010')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='0101')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='0011')
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla_qubits[idx], ctrl_state='0000')
