```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    match = ancilla_qubits[:5]
    flag = ancilla_qubits[5]

    for i in range(5):
        qc.mcx(
            [problem_qubits[i + 1], problem_qubits[i + 2], problem_qubits[i + 3]],
            match[i],
        )

    for qubit in match:
        qc.x(qubit)
    qc.mcx(match, flag)
    for qubit in match:
        qc.x(qubit)
    qc.x(flag)

    qc.z(flag)

    qc.x(flag)
    for qubit in match:
        qc.x(qubit)
    qc.mcx(match, flag)
    for qubit in match:
        qc.x(qubit)

    for i in reversed(range(5)):
        qc.mcx(
            [problem_qubits[i + 1], problem_qubits[i + 2], problem_qubits[i + 3]],
            match[i],
        )
```
