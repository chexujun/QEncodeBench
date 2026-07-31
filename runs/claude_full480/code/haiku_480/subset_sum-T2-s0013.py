from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3, a4 = ancilla_qubits
    p0, p1, p2, p3 = problem_qubits
    
    # Condition 1: x0=1, x1=1, x2=0, x3=1 (sum = 7+10+5 = 22)
    qc.x(p2)
    qc.mcx([p0, p1, p2, p3], a0)
    qc.x(p2)
    
    # Condition 2: x0=0, x1=1, x2=1, x3=1 (sum = 10+7+5 = 22)
    qc.x(p0)
    qc.mcx([p0, p1, p2, p3], a1)
    qc.x(p0)
    
    # Compute OR: a2 = a0 OR a1 via a3 = a0 AND a1
    qc.ccx(a0, a1, a3)
    qc.cx(a0, a2)
    qc.cx(a1, a2)
    qc.cx(a3, a2)
    
    # Apply phase
    qc.z(a2)
    
    # Uncompute OR
    qc.cx(a3, a2)
    qc.cx(a1, a2)
    qc.cx(a0, a2)
    qc.ccx(a0, a1, a3)
    
    # Uncompute conditions
    qc.x(p0)
    qc.mcx([p0, p1, p2, p3], a1)
    qc.x(p0)
    qc.x(p2)
    qc.mcx([p0, p1, p2, p3], a0)
    qc.x(p2)
