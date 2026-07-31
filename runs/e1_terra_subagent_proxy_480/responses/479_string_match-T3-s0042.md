```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    terms = ancilla_qubits[:5]
    result = ancilla_qubits[5]

    for offset, target in enumerate(terms):
        zeros = [
            problem_qubits[offset],
            problem_qubits[offset + 2],
            problem_qubits[offset + 3],
        ]
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(zeros, target)
        for qubit in zeros:
            qc.x(qubit)

    qc.x(result)
    for qubit in terms:
        qc.x(qubit)
    qc.mcx(terms, result)
    for qubit in terms:
        qc.x(qubit)

    qc.z(result)

    for qubit in terms:
        qc.x(qubit)
    qc.mcx(terms, result)
    for qubit in terms:
        qc.x(qubit)
    qc.x(result)

    for offset, target in reversed(list(enumerate(terms))):
        zeros = [
            problem_qubits[offset],
            problem_qubits[offset + 2],
            problem_qubits[offset + 3],
        ]
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(zeros, target)
        for qubit in zeros:
            qc.x(qubit)
```
