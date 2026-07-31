```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:5]
    result = ancilla_qubits[5]

    # Compute one flag for each possible offset. Since the wildcard is the
    # fourth pattern character, a match requires only three consecutive 1s.
    for offset, flag in enumerate(flags):
        qc.mcx(
            [problem_qubits[offset],
             problem_qubits[offset + 1],
             problem_qubits[offset + 2]],
            flag,
        )

    # Compute result = OR(flags) using De Morgan's law.
    qc.x(result)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    for flag in reversed(flags):
        qc.x(flag)

    qc.z(result)

    # Uncompute the OR.
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    for flag in reversed(flags):
        qc.x(flag)
    qc.x(result)

    # Uncompute all offset-match flags.
    for offset in reversed(range(5)):
        qc.mcx(
            [problem_qubits[offset],
             problem_qubits[offset + 1],
             problem_qubits[offset + 2]],
            flags[offset],
        )
```
