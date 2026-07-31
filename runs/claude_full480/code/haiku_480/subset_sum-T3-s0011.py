from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for subset sum: mark when selected elements sum to 10.
    
    Given a = [10, 12, 3, 15, 13] and target T = 10:
    Only the subset {10} sums to 10, which corresponds to the state
    where problem_qubits[0] = 1 and all others = 0 (basis state |00001>).
    
    The oracle applies phase -1 to this state using the condition:
    p0 AND NOT p1 AND NOT p2 AND NOT p3 AND NOT p4
    """
    result = ancilla_qubits[0]
    
    # Flip problem qubits that should be 0 in the marked state
    for i in [1, 2, 3, 4]:
        qc.x(problem_qubits[i])
    
    # Multi-controlled X: result = p0 AND NOT p1 AND NOT p2 AND NOT p3 AND NOT p4
    qc.mcx(problem_qubits, result)
    
    # Apply phase if condition is satisfied
    qc.z(result)
    
    # Uncompute: reverse the multi-controlled X
    qc.mcx(problem_qubits, result)
    
    # Restore problem qubits to original state
    for i in [1, 2, 3, 4]:
        qc.x(problem_qubits[i])
