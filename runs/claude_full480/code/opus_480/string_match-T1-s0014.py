from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0?1?"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']
    ctrls = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
        ctrls.append(q)
    if len(ctrls) == 1:
        qc.z(ctrls[0])
    elif len(ctrls) == 2:
        qc.cz(ctrls[0], ctrls[1])
    else:
        qc.h(ctrls[-1])
        qc.mcx(ctrls[:-1], ctrls[-1])
        qc.h(ctrls[-1])
    for i, bit in fixed:
        if bit == 0:
            qc.x(problem_qubits[i])
