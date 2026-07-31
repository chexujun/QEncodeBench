```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    target = ancilla_qubits[0]
    matches = ancilla_qubits[1:6]

    def compute_match(offset: int, work: int) -> None:
        zeros = [problem_qubits[offset + 1], problem_qubits[offset + 3]]
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(problem_qubits[offset:offset + 4], work)
        for qubit in reversed(zeros):
            qc.x(qubit)

    for offset, work in enumerate(matches):
        compute_match(offset, work)

    qc.x(target)
    for work in matches:
        qc.x(work)
    qc.mcx(matches, target)
    for work in reversed(matches):
        qc.x(work)

    for offset, work in reversed(list(enumerate(matches))):
        compute_match(offset, work)
```
