```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    match_flags = ancilla_qubits[:5]

    # Compute one flag for each possible offset. A match requires 1,0,0,1.
    for offset, flag in enumerate(match_flags):
        controls = problem_qubits[offset:offset + 4]
        qc.x(controls[1])
        qc.x(controls[2])
        qc.mcx(controls, flag)
        qc.x(controls[2])
        qc.x(controls[1])

    # Apply -1 when no offset matches. This is equivalent, up to an
    # irrelevant global phase, to applying -1 exactly when a match exists.
    for flag in match_flags:
        qc.x(flag)
    qc.h(match_flags[4])
    qc.mcx(match_flags[:4], match_flags[4])
    qc.h(match_flags[4])
    for flag in reversed(match_flags):
        qc.x(flag)

    # Uncompute all match flags.
    for offset in reversed(range(5)):
        flag = match_flags[offset]
        controls = problem_qubits[offset:offset + 4]
        qc.x(controls[1])
        qc.x(controls[2])
        qc.mcx(controls, flag)
        qc.x(controls[2])
        qc.x(controls[1])
```
