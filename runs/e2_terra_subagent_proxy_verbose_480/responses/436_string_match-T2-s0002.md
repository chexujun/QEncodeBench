```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    m0, m1, m2, phase = ancilla_qubits

    def compute_match(offset, target):
        qc.x(problem_qubits[offset + 2])  # pattern's final 0 control
        qc.mcx(
            [problem_qubits[offset], problem_qubits[offset + 1],
             problem_qubits[offset + 2]],
            target
        )
        qc.x(problem_qubits[offset + 2])

    # Compute whether "110" occurs at each possible offset.
    compute_match(0, m0)
    compute_match(1, m1)
    compute_match(2, m2)

    # Phase-flip the no-match state; this differs from flipping any-match
    # only by an irrelevant global phase.
    qc.x(m0)
    qc.x(m1)
    qc.x(m2)
    qc.h(phase)
    qc.mcx([m0, m1, m2], phase)
    qc.h(phase)
    qc.x(m2)
    qc.x(m1)
    qc.x(m0)

    # Uncompute match flags.
    compute_match(2, m2)
    compute_match(1, m1)
    compute_match(0, m0)
```
