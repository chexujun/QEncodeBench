from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Compute NOT(x0 AND x1) into a0
    qc.x(a0)
    qc.ccx(x0, x1, a0)
    
    # Compute NOT(x0 AND x2) into a1
    qc.x(a1)
    qc.ccx(x0, x2, a1)
    
    # Compute NOT(x1 AND x2) into a2
    qc.x(a2)
    qc.ccx(x1, x2, a2)
    
    # Compute a0 AND a1 into a3
    qc.ccx(a0, a1, a3)
    
    # Compute a3 AND a2 into a4
    qc.ccx(a3, a2, a4)
    
    # Compute a4 AND x3 into a5 (the oracle bit)
    qc.ccx(a4, x3, a5)
    
    # Apply phase
    qc.z(a5)
    
    # Uncompute in reverse
    qc.ccx(a4, x3, a5)
    qc.ccx(a3, a2, a4)
    qc.ccx(a0, a1, a3)
    qc.ccx(x1, x2, a2)
    qc.x(a2)
    qc.ccx(x0, x2, a1)
    qc.x(a1)
    qc.ccx(x0, x1, a0)
    qc.x(a0)
