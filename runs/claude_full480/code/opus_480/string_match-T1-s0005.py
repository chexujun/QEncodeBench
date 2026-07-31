from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1??10?"
    fixed = [(i, c) for i, c in enumerate(pattern) if c in "01"]
    ctrls = []
    for i, c in fixed:
        q = problem_qubits[i]
        if c == "0":
            qc.x(q)
        ctrls.append(q)
    target = ctrls[-1]
    controls = ctrls[:-1]
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)
    for i, c in fixed:
        if c == "0":
            qc.x(problem_qubits[i])
