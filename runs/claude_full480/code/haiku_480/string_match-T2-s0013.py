from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    
    # Offset 0: check s_0=1, s_1=1, s_3=0, s_4=1
    qc.x(q[3])
    qc.mcx([q[0], q[1], q[3], q[4]], a1)
    qc.x(q[3])
    
    # Offset 1: check s_1=1, s_2=1, s_4=0, s_5=1
    qc.x(q[4])
    qc.mcx([q[1], q[2], q[4], q[5]], a2)
    qc.x(q[4])
    
    # Offset 2: check s_2=1, s_3=1, s_5=0, s_6=1
    qc.x(q[5])
    qc.mcx([q[2], q[3], q[5], q[6]], a3)
    qc.x(q[5])
    
    # Compute OR via De Morgan: a0 = NOT(NOT a1 AND NOT a2 AND NOT a3)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.mcx([a1, a2, a3], a0)
    qc.x(a0)
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    
    # Apply phase
    qc.z(a0)
    
    # Uncompute OR
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a0)
    qc.mcx([a1, a2, a3], a0)
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    
    # Uncompute offset 2
    qc.x(q[5])
    qc.mcx([q[2], q[3], q[5], q[6]], a3)
    qc.x(q[5])
    
    # Uncompute offset 1
    qc.x(q[4])
    qc.mcx([q[1], q[2], q[4], q[5]], a2)
    qc.x(q[4])
    
    # Uncompute offset 0
    qc.x(q[3])
    qc.mcx([q[0], q[1], q[3], q[4]], a1)
    qc.x(q[3])
