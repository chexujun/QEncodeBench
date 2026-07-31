```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]
    flag = ancilla_qubits[5]

    # Compute the five offset-match predicates:
    # match[o] = s[o] AND s[o+1] AND NOT s[o+3].
    for o, target in enumerate(matches):
        qc.x(problem_qubits[o + 3])
        qc.mcx(
            [problem_qubits[o], problem_qubits[o + 1],
             problem_qubits[o + 3]],
            target,
        )
        qc.x(problem_qubits[o + 3])

    # Compute flag = OR(matches) using De Morgan's law.
    qc.x(flag)
    for target in matches:
        qc.x(target)
    qc.mcx(matches, flag)
    for target in reversed(matches):
        qc.x(target)

    qc.z(flag)

    # Uncompute the OR flag.
    for target in matches:
        qc.x(target)
    qc.mcx(matches, flag)
    for target in reversed(matches):
        qc.x(target)
    qc.x(flag)

    # Uncompute all offset-match predicates.
    for o in reversed(range(5)):
        target = matches[o]
        qc.x(problem_qubits[o + 3])
        qc.mcx(
            [problem_qubits[o], problem_qubits[o + 1],
             problem_qubits[o + 3]],
            target,
        )
        qc.x(problem_qubits[o + 3])
```
