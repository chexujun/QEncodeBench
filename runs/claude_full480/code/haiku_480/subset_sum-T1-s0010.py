from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2 = problem_qubits
    a = ancilla_qubits[0]
    b = ancilla_qubits[1]
    
    # Identify which state has sum = 6:
    # 5*x0 + 6*x1 + 3*x2 = 6 only when x0=0, x1=1, x2=0
    # Condition: (NOT q0) AND q1 AND (NOT q2)
    
    # Compute indicator into ancilla using Toffoli gates
    qc.x(q0)
    qc.x(q2)
    qc.ccx(q0, q1, b)      # b = q0 AND q1
    qc.ccx(b, q2, a)       # a = b AND q2 = (NOT q0_orig) AND q1 AND (NOT q2_orig)
    
    # Apply phase: Z gate encodes -1 phase when a=1
    qc.z(a)
    
    # Uncompute to restore ancillas to |0>
    qc.ccx(b, q2, a)
    qc.ccx(q0, q1, b)
    qc.x(q2)
    qc.x(q0)
