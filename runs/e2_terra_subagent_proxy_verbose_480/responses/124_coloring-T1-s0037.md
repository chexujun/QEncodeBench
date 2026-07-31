```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]
    edges = ((0, 1), (0, 2), (1, 2), (1, 3))

    def compute_conflict(v, w, target):
        low_v = problem_qubits[2 * v]
        high_v = problem_qubits[2 * v + 1]
        low_w = problem_qubits[2 * w]
        high_w = problem_qubits[2 * w + 1]

        # Convert low bits to low XOR high.  This is 0 precisely for
        # color 0 (codes 00 and 11), and 1 for colors 1 and 2.
        qc.cx(high_v, low_v)
        qc.cx(high_w, low_w)

        # Both vertices have color 0.
        qc.x(low_v)
        qc.x(low_w)
        qc.ccx(low_v, low_w, target)
        qc.x(low_w)
        qc.x(low_v)

        # Both have a nonzero color, equal to 1 (high bits both 0).
        qc.x(high_v)
        qc.x(high_w)
        qc.mcx([low_v, high_v, low_w, high_w], target)
        qc.x(high_w)
        qc.x(high_v)

        # Both have a nonzero color, equal to 2 (high bits both 1).
        qc.mcx([low_v, high_v, low_w, high_w], target)

        qc.cx(high_w, low_w)
        qc.cx(high_v, low_v)

    for (v, w), flag in zip(edges, flags):
        compute_conflict(v, w, flag)

    # A valid coloring has no conflict flag set.
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(flags, phase_ancilla)
    for flag in reversed(flags):
        qc.x(flag)

    for (v, w), flag in reversed(list(zip(edges, flags))):
        compute_conflict(v, w, flag)
```
