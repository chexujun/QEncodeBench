```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    match_flags = ancilla_qubits[:5]

    # Compute one match flag for each possible offset.
    for offset, flag in enumerate(match_flags):
        controls = problem_qubits[offset:offset + 4]
        qc.x(controls[1])
        qc.x(controls[3])
        qc.mcx(controls, flag)
        qc.x(controls[3])
        qc.x(controls[1])

    # Apply -1 to the no-match states. Up to an irrelevant global phase,
    # this is exactly a -1 phase on states having at least one match.
    for flag in match_flags:
        qc.x(flag)
    qc.mcp(pi, match_flags)
    for flag in reversed(match_flags):
        qc.x(flag)

    # Uncompute all match flags.
    for offset in reversed(range(5)):
        flag = match_flags[offset]
        controls = problem_qubits[offset:offset + 4]
        qc.x(controls[1])
        qc.x(controls[3])
        qc.mcx(controls, flag)
        qc.x(controls[3])
        qc.x(controls[1])
```
