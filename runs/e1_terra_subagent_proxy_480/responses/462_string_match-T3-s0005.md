```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:6]
    output = ancilla_qubits[6]

    for offset, flag in enumerate(flags):
        window = problem_qubits[offset:offset + 3]
        for qubit in window:
            qc.x(qubit)
        qc.mcx(window, flag)
        for qubit in window:
            qc.x(qubit)

    for flag in flags:
        qc.x(flag)
    qc.x(output)
    qc.mcx(flags, output)
    qc.x(output)
    for flag in flags:
        qc.x(flag)

    qc.z(output)

    for flag in flags:
        qc.x(flag)
    qc.x(output)
    qc.mcx(flags, output)
    qc.x(output)
    for flag in flags:
        qc.x(flag)

    for offset, flag in reversed(list(enumerate(flags))):
        window = problem_qubits[offset:offset + 3]
        for qubit in window:
            qc.x(qubit)
        qc.mcx(window, flag)
        for qubit in window:
            qc.x(qubit)
```
