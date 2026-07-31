from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits[0:4]
    a0, a1, a2, a3, a4 = ancilla_qubits[0:5]
    
    # Compute: a0 = q0
    qc.cx(q0, a0)
    
    # Compute: a1 = NOT q1
    qc.x(q1)
    qc.cx(q1, a1)
    qc.x(q1)
    
    # Compute: a2 = a0 AND a1 (represents q0 AND (NOT q1))
    qc.ccx(a0, a1, a2)
    
    # Compute: a3 = NOT q2
    qc.x(q2)
    qc.cx(q2, a3)
    qc.x(q2)
    
    # Compute: a4 = a2 AND a3 (represents (q0 AND (NOT q1)) AND (NOT q2))
    qc.ccx(a2, a3, a4)
    
    # Phase: flip phase if condition is satisfied
    qc.z(a4)
    
    # Uncompute: reverse in opposite order
    qc.ccx(a2, a3, a4)
    qc.x(q2)
    qc.cx(q2, a3)
    qc.x(q2)
    qc.ccx(a0, a1, a2)
    qc.x(q1)
    qc.cx(q1, a1)
    qc.x(q1)
    qc.cx(q0, a0)
