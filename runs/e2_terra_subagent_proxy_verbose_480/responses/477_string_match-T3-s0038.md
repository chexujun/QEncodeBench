```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]
    result = ancilla_qubits[5]

    # Compute one flag for each possible offset. The pattern is 1, 1, 0, 1.
    for offset, flag in enumerate(flags):
        zero_bit = problem_qubits[offset + 2]
        controls = problem_qubits[offset:offset + 4]
        qc.x(zero_bit)
        qc.mcx(controls, flag)
        qc.x(zero_bit)

    # Compute result = OR(flags) using De Morgan's law.
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    qc.x(result)
    for flag in reversed(flags):
        qc.x(flag)

    # Apply the phase exactly when at least one offset matches.
    qc.z(result)

    # Uncompute the OR.
    for flag in flags:
        qc.x(flag)
    qc.x(result)
    qc.mcx(flags, result)
    for flag in reversed(flags):
        qc.x(flag)

    # Uncompute all match flags.
    for offset in reversed(range(5)):
        flag = flags[offset]
        zero_bit = problem_qubits[offset + 2]
        controls = problem_qubits[offset:offset + 4]
        qc.x(zero_bit)
        qc.mcx(controls, flag)
        qc.x(zero_bit)
```
