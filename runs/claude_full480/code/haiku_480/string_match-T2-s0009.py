from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Compute offset 0: s_0=1 AND s_1=1 AND s_3=1 AND s_4=0
    qc.x(q[4])
    qc.mcx([q[0], q[1], q[3], q[4]], a[0])
    qc.x(q[4])
    
    # Compute offset 1: s_1=1 AND s_2=1 AND s_4=1 AND s_5=0
    qc.x(q[5])
    qc.mcx([q[1], q[2], q[4], q[5]], a[1])
    qc.x(q[5])
    
    # Compute offset 2: s_2=1 AND s_3=1 AND s_5=1 AND s_6=0
    qc.x(q[6])
    qc.mcx([q[2], q[3], q[5], q[6]], a[2])
    qc.x(q[6])
    
    # Compute OR: a[3] = a[0] OR a[1] OR a[2]
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    
    # Apply phase -1 if any pattern matches
    qc.p(math.pi, a[3])
    
    # Uncompute OR
    qc.x(a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    
    # Uncompute offset 2
    qc.x(q[6])
    qc.mcx([q[2], q[3], q[5], q[6]], a[2])
    qc.x(q[6])
    
    # Uncompute offset 1
    qc.x(q[5])
    qc.mcx([q[1], q[2], q[4], q[5]], a[1])
    qc.x(q[5])
    
    # Uncompute offset 0
    qc.x(q[4])
    qc.mcx([q[0], q[1], q[3], q[4]], a[0])
    qc.x(q[4])
