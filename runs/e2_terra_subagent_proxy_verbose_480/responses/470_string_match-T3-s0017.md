```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    matches = ancilla_qubits[:5]

    # Compute the five possible matches:
    # offset o matches "?111" iff s[o+1], s[o+2], and s[o+3] are all 1.
    for offset in range(5):
        qc.mcx(
            [problem_qubits[offset + 1],
             problem_qubits[offset + 2],
             problem_qubits[offset + 3]],
            matches[offset],
        )

    # Apply -1 when none of the offsets match. Up to an irrelevant global
    # phase, this is exactly -1 when at least one offset matches.
    for qubit in matches:
        qc.x(qubit)
    qc.h(matches[4])
    qc.mcx(matches[:4], matches[4])
    qc.h(matches[4])
    for qubit in reversed(matches):
        qc.x(qubit)

    # Uncompute every match ancilla.
    for offset in reversed(range(5)):
        qc.mcx(
            [problem_qubits[offset + 1],
             problem_qubits[offset + 2],
             problem_qubits[offset + 3]],
            matches[offset],
        )
```
