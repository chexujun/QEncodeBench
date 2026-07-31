```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]
    flag = ancilla_qubits[5]

    # Compute the five offset-match predicates:
    # match[o] = s[o] AND NOT s[o+2] AND NOT s[o+3].
    for offset, target in enumerate(matches):
        q2 = problem_qubits[offset + 2]
        q3 = problem_qubits[offset + 3]
        qc.x(q2)
        qc.x(q3)
        qc.mcx(
            [problem_qubits[offset], q2, q3],
            target,
        )
        qc.x(q3)
        qc.x(q2)

    # Compute flag = 1 exactly when none of the offsets matches.
    # Phasing the complement differs from phasing the desired OR only by
    # an irrelevant global phase.
    for qubit in matches:
        qc.x(qubit)
    qc.mcx(matches, flag)
    for qubit in reversed(matches):
        qc.x(qubit)

    qc.z(flag)

    # Uncompute the complement flag.
    for qubit in matches:
        qc.x(qubit)
    qc.mcx(matches, flag)
    for qubit in reversed(matches):
        qc.x(qubit)

    # Uncompute all offset-match predicates.
    for offset in reversed(range(5)):
        target = matches[offset]
        q2 = problem_qubits[offset + 2]
        q3 = problem_qubits[offset + 3]
        qc.x(q2)
        qc.x(q3)
        qc.mcx(
            [problem_qubits[offset], q2, q3],
            target,
        )
        qc.x(q3)
        qc.x(q2)
```
