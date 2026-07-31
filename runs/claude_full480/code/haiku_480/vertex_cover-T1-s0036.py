from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    result = ancilla_qubits[0]
    a1, a2, a3, a4, a5, a6 = ancilla_qubits[1:]
    
    # Compute term1: x0 AND x1 AND NOT x2 AND NOT x3
    qc.ccx(x0, x1, a1)
    qc.x(x2)
    qc.ccx(a1, x2, a2)
    qc.x(x2)
    qc.x(x3)
    qc.ccx(a2, x3, a3)
    qc.x(x3)
    
    # Compute term2: x0 AND NOT x1 AND NOT x2 AND x3
    qc.x(x1)
    qc.ccx(x0, x1, a4)
    qc.x(x1)
    qc.x(x2)
    qc.ccx(a4, x2, a5)
    qc.x(x2)
    qc.ccx(a5, x3, a6)
    
    # Compute result = term1 OR term2
    qc.x(a3)
    qc.x(a6)
    qc.ccx(a3, a6, result)
    qc.x(result)
    qc.x(a6)
    qc.x(a3)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute result = term1 OR term2
    qc.x(a3)
    qc.x(a6)
    qc.x(result)
    qc.ccx(a3, a6, result)
    qc.x(a6)
    qc.x(a3)
    
    # Uncompute term2
    qc.ccx(a5, x3, a6)
    qc.x(x2)
    qc.ccx(a4, x2, a5)
    qc.x(x2)
    qc.x(x1)
    qc.ccx(x0, x1, a4)
    qc.x(x1)
    
    # Uncompute term1
    qc.x(x3)
    qc.ccx(a2, x3, a3)
    qc.x(x3)
    qc.x(x2)
    qc.ccx(a1, x2, a2)
    qc.x(x2)
    qc.ccx(x0, x1, a1)
