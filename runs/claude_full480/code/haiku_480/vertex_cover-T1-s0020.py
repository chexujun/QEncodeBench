from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for vertex cover problem on 4-vertex graph with edges
    (0,1), (0,2), (1,2), (1,3), (2,3).
    Phases states representing valid vertex covers of size <= 2.
    The only valid cover is {1,2}, corresponding to state (x0=0, x1=1, x2=1, x3=0).
    """
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a = ancilla_qubits
    
    # Compute the predicate: marker = (NOT x0) AND x1 AND x2 AND (NOT x3)
    # This is true only for the unique valid vertex cover
    
    # Compute NOT x0 into a[0]
    qc.x(a[0])
    qc.cx(x0, a[0])
    
    # Compute NOT x3 into a[1]
    qc.x(a[1])
    qc.cx(x3, a[1])
    
    # AND chain to compute full predicate
    qc.ccx(a[0], x1, a[2])  # a[2] = a[0] AND x1
    qc.ccx(a[2], x2, a[3])  # a[3] = a[2] AND x2
    qc.ccx(a[3], a[1], a[4])  # a[4] = a[3] AND a[1]
    
    # Apply phase -1 to valid states
    qc.z(a[4])
    
    # Uncompute in reverse order
    qc.ccx(a[3], a[1], a[4])
    qc.ccx(a[2], x2, a[3])
    qc.ccx(a[0], x1, a[2])
    
    # Uncompute NOT x3
    qc.cx(x3, a[1])
    qc.x(a[1])
    
    # Uncompute NOT x0
    qc.cx(x0, a[0])
    qc.x(a[0])
