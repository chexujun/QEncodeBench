```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]
    flag = ancilla_qubits[5]

    # Compute one match bit for each possible offset:
    # match[o] = s[o] AND NOT(s[o+1]) AND s[o+2].
    for offset, match in enumerate(matches):
        qc.x(problem_qubits[offset + 1])
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
            ],
            match,
        )
        qc.x(problem_qubits[offset + 1])

    # Compute flag = OR(matches) using De Morgan's law.
    qc.x(flag)
    for match in matches:
        qc.x(match)
    qc.mcx(matches, flag)
    for match in reversed(matches):
        qc.x(match)

    qc.z(flag)

    # Uncompute the OR flag.
    for match in matches:
        qc.x(match)
    qc.mcx(matches, flag)
    for match in reversed(matches):
        qc.x(match)
    qc.x(flag)

    # Uncompute all match bits.
    for offset in reversed(range(5)):
        qc.x(problem_qubits[offset + 1])
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
            ],
            matches[offset],
        )
        qc.x(problem_qubits[offset + 1])
```
