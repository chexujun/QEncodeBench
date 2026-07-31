from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    p = problem_qubits
    
    # COMPUTE: Offset 0 condition (s_0=0, s_1=0, s_2=1, s_5=0)
    qc.x(p[0])
    qc.x(p[1])
    qc.x(p[5])
    qc.mcx([p[0], p[1], p[2], p[5]], a0)
    qc.x(p[5])
    qc.x(p[1])
    qc.x(p[0])
    
    # COMPUTE: Offset 1 condition (s_1=0, s_2=0, s_3=1, s_6=0)
    qc.x(p[1])
    qc.x(p[2])
    qc.x(p[6])
    qc.mcx([p[1], p[2], p[3], p[6]], a1)
    qc.x(p[6])
    qc.x(p[2])
    qc.x(p[1])
    
    # COMPUTE: OR of a0 and a1 into a2
    qc.x(a2)
    qc.cx(a0, a2)
    qc.cx(a1, a2)
    qc.x(a2)
    
    # PHASE: Apply -1 phase to marked states
    qc.z(a2)
    
    # UNCOMPUTE: OR
    qc.x(a2)
    qc.cx(a1, a2)
    qc.cx(a0, a2)
    qc.x(a2)
    
    # UNCOMPUTE: Offset 1 condition
    qc.x(p[1])
    qc.x(p[2])
    qc.x(p[6])
    qc.mcx([p[1], p[2], p[3], p[6]], a1)
    qc.x(p[6])
    qc.x(p[2])
    qc.x(p[1])
    
    # UNCOMPUTE: Offset 0 condition
    qc.x(p[0])
    qc.x(p[1])
    qc.x(p[5])
    qc.mcx([p[0], p[1], p[2], p[5]], a0)
    qc.x(p[5])
    qc.x(p[1])
    qc.x(p[0])
