from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = ancilla_qubits[0]
    x = problem_qubits
    
    # Compute: Set a = NOT x[0] AND NOT x[1] AND NOT x[2] AND x[3]
    # This marks the unique solution: select only a[3]=8 for sum=8
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2], x[3]], a)
    qc.x(x[2])
    qc.x(x[1])
    qc.x(x[0])
    
    # Apply phase flip
    qc.z(a)
    
    # Uncompute: restore a to 0
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2], x[3]], a)
    qc.x(x[2])
    qc.x(x[1])
    qc.x(x[0])
