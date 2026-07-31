from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    
    # Compute a0 = NOT x1
    qc.x(x1)
    qc.cx(x1, a0)
    qc.x(x1)
    
    # Compute a1 = NOT x2
    qc.x(x2)
    qc.cx(x2, a1)
    qc.x(x2)
    
    # Compute a2 = x0 AND a0 (i.e., x0 AND NOT x1)
    qc.ccx(x0, a0, a2)
    
    # Compute a3 = a2 AND a1 (i.e., x0 AND NOT x1 AND NOT x2)
    qc.ccx(a2, a1, a3)
    
    # Apply phase when a3 = 1
    qc.z(a3)
    
    # Uncompute: reverse of above
    qc.ccx(a2, a1, a3)
    qc.ccx(x0, a0, a2)
    
    # Uncomputations for NOT x2
    qc.x(x2)
    qc.cx(x2, a1)
    qc.x(x2)
    
    # Uncomputations for NOT x1
    qc.x(x1)
    qc.cx(x1, a0)
    qc.x(x1)
