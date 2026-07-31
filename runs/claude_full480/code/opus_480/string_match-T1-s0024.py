from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "10010"
    a = ancilla_qubits[0]

    # Flip fixed-pattern qubits so that a match => all controls are |1>
    flip = [i for i, c in enumerate(pattern) if c == '0']
    controls = [problem_qubits[i] for i, c in enumerate(pattern) if c != '?']

    for i in flip:
        qc.x(problem_qubits[i])

    # Phase -1 iff all specified positions match (all controls are 1)
    qc.h(a)
    qc.mcx(controls, a)
    qc.h(a)

    for i in flip:
        qc.x(problem_qubits[i])
