from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute offset 0 match into a[1]
    # Pattern at offset 0: x[0]=0, x[1]=1, x[2]=0, x[3]=1
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2], x[3]], a[1])
    qc.x(x[2])
    qc.x(x[0])
    
    # Compute offset 1 match into a[2]
    # Pattern at offset 1: x[1]=0, x[2]=1, x[3]=0, x[4]=1
    qc.x(x[1])
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3], x[4]], a[2])
    qc.x(x[3])
    qc.x(x[1])
    
    # Compute OR: a[0] = a[1] OR a[2]
    qc.ccx(a[1], a[2], a[0])
    qc.cx(a[1], a[0])
    qc.cx(a[2], a[0])
    
    # Apply phase
    qc.z(a[0])
    
    # Uncompute in reverse order
    qc.cx(a[2], a[0])
    qc.cx(a[1], a[0])
    qc.ccx(a[1], a[2], a[0])
    
    # Uncompute offset 1 match
    qc.x(x[1])
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3], x[4]], a[2])
    qc.x(x[3])
    qc.x(x[1])
    
    # Uncompute offset 0 match
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2], x[3]], a[1])
    qc.x(x[2])
    qc.x(x[0])
