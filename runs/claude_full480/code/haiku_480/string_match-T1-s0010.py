from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s0 = problem_qubits[0]
    s1 = problem_qubits[1]
    s3 = problem_qubits[3]
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    
    # Compute (NOT s_0) AND s_1 into a0
    qc.x(s0)
    qc.ccx(s0, s1, a0)
    qc.x(s0)
    
    # Compute ((NOT s_0) AND s_1) AND s_3 into a1
    qc.ccx(a0, s3, a1)
    
    # Apply phase -1 when predicate is true
    qc.z(a1)
    
    # Uncompute to restore ancillas to |0>
    qc.ccx(a0, s3, a1)
    
    qc.x(s0)
    qc.ccx(s0, s1, a0)
    qc.x(s0)
