```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    matches = ancilla_qubits[:5]
    target = ancilla_qubits[5]

    for offset, work in enumerate(matches):
        zeros = (problem_qubits[offset], problem_qubits[offset + 3])
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
                problem_qubits[offset + 3],
            ],
            work,
        )
        for qubit in zeros:
            qc.x(qubit)

    qc.x(matches)
    qc.mcx(matches, target)
    qc.x(matches)
    qc.x(target)

    for offset, work in reversed(list(enumerate(matches))):
        zeros = (problem_qubits[offset], problem_qubits[offset + 3])
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
                problem_qubits[offset + 3],
            ],
            work,
        )
        for qubit in zeros:
            qc.x(qubit)
```
