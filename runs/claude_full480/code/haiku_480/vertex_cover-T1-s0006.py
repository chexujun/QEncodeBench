def build_oracle(qc, problem_qubits, ancilla_qubits):
    not_x0 = ancilla_qubits[0]
    and_not_x0_x1 = ancilla_qubits[1]
    not_x2 = ancilla_qubits[2]
    condition = ancilla_qubits[3]
    phase_marker = ancilla_qubits[4]
    
    qc.x(not_x0)
    qc.cx(problem_qubits[0], not_x0)
    qc.ccx(not_x0, problem_qubits[1], and_not_x0_x1)
    qc.x(not_x2)
    qc.cx(problem_qubits[2], not_x2)
    qc.ccx(and_not_x0_x1, not_x2, condition)
    qc.ccx(condition, problem_qubits[3], phase_marker)
    qc.z(phase_marker)
    qc.ccx(condition, problem_qubits[3], phase_marker)
    qc.ccx(and_not_x0_x1, not_x2, condition)
    qc.cx(problem_qubits[2], not_x2)
    qc.x(not_x2)
    qc.ccx(not_x0, problem_qubits[1], and_not_x0_x1)
    qc.cx(problem_qubits[0], not_x0)
    qc.x(not_x0)
