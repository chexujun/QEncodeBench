```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    output = ancilla_qubits[0]
    flags = ancilla_qubits[1:6]

    def mark_occurrence(offset: int, target: int) -> None:
        controls = problem_qubits[offset:offset + 4]
        for index in (0, 2, 3):
            qc.x(controls[index])
        qc.mcx(controls, target)
        for index in (0, 2, 3):
            qc.x(controls[index])

    for offset, flag in enumerate(flags):
        mark_occurrence(offset, flag)

    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, output)
    for flag in flags:
        qc.x(flag)

    for offset, flag in reversed(list(enumerate(flags))):
        mark_occurrence(offset, flag)
```
