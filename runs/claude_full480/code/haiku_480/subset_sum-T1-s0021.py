from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for subset sum: a = [6, 6, 4], target T = 4.
    Only state |001⟩ (select a[2]=4) satisfies the constraint.
    Applies phase -1 to |001⟩ by computing (NOT x0) AND (NOT x1) AND x2.
    """
    x0, x1, x2 = problem_qubits
    a, b = ancilla_qubits[0], ancilla_qubits[1]
    
    # Flip x0 and x1 to compute NOT x0 and NOT x1
    qc.x(x0)
    qc.x(x1)
    
    # Compute temp = x0 AND x1 into ancilla a
    qc.ccx(x0, x1, a)
    
    # Compute result = temp AND x2 into ancilla b
    qc.ccx(a, x2, b)
    
    # Apply phase flip
    qc.z(b)
    
    # Uncompute: reverse the operations
    qc.ccx(a, x2, b)
    qc.ccx(x0, x1, a)
    
    # Flip back x0 and x1
    qc.x(x1)
    qc.x(x0)
