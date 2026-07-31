from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Offset 0: check p[0]=1, p[1]=0, p[2]=1, p[3]=1
    qc.x(p[1])
    qc.mcx([p[0], p[1], p[2], p[3]], a[0])
    qc.x(p[1])
    
    # Offset 1: check p[1]=1, p[2]=0, p[3]=1, p[4]=1
    qc.x(p[2])
    qc.mcx([p[1], p[2], p[3], p[4]], a[1])
    qc.x(p[2])
    
    # Offset 2: check p[2]=1, p[3]=0, p[4]=1, p[5]=1
    qc.x(p[3])
    qc.mcx([p[2], p[3], p[4], p[5]], a[2])
    qc.x(p[3])
    
    # Compute OR of the three matches in a[3]
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.x(a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    
    # Apply phase
    qc.z(a[3])
    
    # Uncompute in reverse (mirror of compute)
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.x(a[2])
    qc.x(a[1])
    qc.x(a[0])
    
    # Offset 2: uncompute
    qc.x(p[3])
    qc.mcx([p[2], p[3], p[4], p[5]], a[2])
    qc.x(p[3])
    
    # Offset 1: uncompute
    qc.x(p[2])
    qc.mcx([p[1], p[2], p[3], p[4]], a[1])
    qc.x(p[2])
    
    # Offset 0: uncompute
    qc.x(p[1])
    qc.mcx([p[0], p[1], p[2], p[3]], a[0])
    qc.x(p[1])
