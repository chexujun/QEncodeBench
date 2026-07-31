from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Marked states: vertex covers of size ≤ 2
    # These are {2,3} (x=12) and {3,4} (x=24)
    # Condition: x_3 AND NOT x_1 AND NOT x_0 AND (x_2 XOR x_4)
    
    p0, p1, p2, p3, p4 = problem_qubits
    a0, a1, a2, a3 = ancilla_qubits[:4]
    
    # Compute x_2 XOR x_4 into a0
    qc.cx(p2, a0)
    qc.cx(p4, a0)
    
    # Compute x_3 AND (x_2 XOR x_4) into a1
    qc.ccx(p3, a0, a1)
    
    # Compute NOT x_1 AND a1 into a2
    qc.x(p1)
    qc.ccx(p1, a1, a2)
    qc.x(p1)
    
    # Compute NOT x_0 AND a2 into a3
    qc.x(p0)
    qc.ccx(p0, a2, a3)
    qc.x(p0)
    
    # Apply phase -1 to marked states
    qc.z(a3)
    
    # Uncompute to restore ancillas to |0>
    qc.x(p0)
    qc.ccx(p0, a2, a3)
    qc.x(p0)
    
    qc.x(p1)
    qc.ccx(p1, a1, a2)
    qc.x(p1)
    
    qc.ccx(p3, a0, a1)
    
    qc.cx(p4, a0)
    qc.cx(p2, a0)
