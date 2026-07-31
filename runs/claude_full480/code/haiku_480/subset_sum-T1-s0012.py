from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits[0:4]
    
    # Identify which subset sums to target 4:
    # 2*x0 + 5*x1 + 4*x2 = 4 has unique solution: x0=0, x1=0, x2=1
    # So mark when NOT(x0) AND NOT(x1) AND x2 = 1
    
    # Compute NOT(x0) into a0
    qc.x(a0)
    qc.cx(problem_qubits[0], a0)
    
    # Compute NOT(x1) into a1
    qc.x(a1)
    qc.cx(problem_qubits[1], a1)
    
    # Compute (NOT(x0) AND NOT(x1)) into a2
    qc.ccx(a0, a1, a2)
    
    # Compute (NOT(x0) AND NOT(x1) AND x2) into a3
    qc.ccx(a2, problem_qubits[2], a3)
    
    # Apply phase flip to mark solutions
    qc.z(a3)
    
    # Uncompute: reverse all operations in opposite order
    qc.ccx(a2, problem_qubits[2], a3)
    qc.ccx(a0, a1, a2)
    qc.cx(problem_qubits[1], a1)
    qc.x(a1)
    qc.cx(problem_qubits[0], a0)
    qc.x(a0)
