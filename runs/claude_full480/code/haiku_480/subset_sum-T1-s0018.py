from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    flag = ancilla_qubits[0]
    
    # Mark only state |011>: x0=1, x1=1, x2=0
    # This is where sum = a[0]*x0 + a[1]*x1 + a[2]*x2 = 1 + 1 + 0 = 2
    
    # Compute: flag = x0 AND x1 AND (NOT x2)
    qc.x(q2)
    qc.mcx([q0, q1, q2], flag)
    qc.x(q2)
    
    # Apply phase
    qc.z(flag)
    
    # Uncompute
    qc.x(q2)
    qc.mcx([q0, q1, q2], flag)
    qc.x(q2)
