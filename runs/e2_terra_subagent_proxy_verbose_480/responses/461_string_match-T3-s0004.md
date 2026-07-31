```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    matches = ancilla_qubits[:5]
    flag = ancilla_qubits[5]

    # Compute whether each of the five possible windows matches 00?1.
    for offset, target in enumerate(matches):
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 1])
        qc.mcx(
            [problem_qubits[offset],
             problem_qubits[offset + 1],
             problem_qubits[offset + 3]],
            target,
        )
        qc.x(problem_qubits[offset + 1])
        qc.x(problem_qubits[offset])

    # flag = 1 exactly when no window matched.  A Z on this flag marks
    # the complement, which differs from the desired oracle only globally.
    for target in matches:
        qc.x(target)
    qc.mcx(matches, flag)
    for target in reversed(matches):
        qc.x(target)

    qc.z(flag)

    # Uncompute the complement flag.
    for target in matches:
        qc.x(target)
    qc.mcx(matches, flag)
    for target in reversed(matches):
        qc.x(target)

    # Uncompute all window-match flags.
    for offset, target in reversed(list(enumerate(matches))):
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 1])
        qc.mcx(
            [problem_qubits[offset],
             problem_qubits[offset + 1],
             problem_qubits[offset + 3]],
            target,
        )
        qc.x(problem_qubits[offset + 1])
        qc.x(problem_qubits[offset])
```
