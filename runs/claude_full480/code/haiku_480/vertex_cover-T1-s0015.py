from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Valid vertex covers of size ≤ 2: {0, 2} and {1, 2}
    # In binary: (1,0,1,0) and (0,1,1,0)
    # Both satisfy: q[2]=1 AND q[3]=0 AND (q[0] XOR q[1])=1
    
    # Compute marker condition: q[2] AND NOT q[3] AND (q[0] XOR q[1])
    
    # a[0] = NOT q[3]
    qc.x(a[0])
    qc.cx(q[3], a[0])
    
    # a[1] = q[0] XOR q[1]
    qc.cx(q[0], a[1])
    qc.cx(q[1], a[1])
    
    # a[2] = q[2] AND a[0]
    qc.mcx([q[2], a[0]], a[2])
    
    # a[4] = a[2] AND a[1]
    qc.mcx([a[2], a[1]], a[4])
    
    # Apply phase -1 if a[4] = 1
    qc.z(a[4])
    
    # Uncompute (reverse of forward pass)
    qc.mcx([a[2], a[1]], a[4])
    qc.mcx([q[2], a[0]], a[2])
    qc.cx(q[1], a[1])
    qc.cx(q[0], a[1])
    qc.cx(q[3], a[0])
    qc.x(a[0])
