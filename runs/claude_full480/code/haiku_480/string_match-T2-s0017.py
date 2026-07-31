from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Offset 0: s[0]=0, s[1]=1, s[2]=0, s[3]=0
    qc.x(q[0])
    qc.x(q[2])
    qc.x(q[3])
    
    qc.mcx([q[0], q[1], q[2], q[3]], a[0])
    qc.z(a[0])
    qc.mcx([q[0], q[1], q[2], q[3]], a[0])
    
    qc.x(q[0])
    qc.x(q[2])
    qc.x(q[3])
    
    # Offset 1: s[1]=0, s[2]=1, s[3]=0, s[4]=0
    qc.x(q[1])
    qc.x(q[3])
    qc.x(q[4])
    
    qc.mcx([q[1], q[2], q[3], q[4]], a[1])
    qc.z(a[1])
    qc.mcx([q[1], q[2], q[3], q[4]], a[1])
    
    qc.x(q[1])
    qc.x(q[3])
    qc.x(q[4])
