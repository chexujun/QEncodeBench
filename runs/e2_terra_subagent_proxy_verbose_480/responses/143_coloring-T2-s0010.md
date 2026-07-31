```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    phase_ancilla = ancilla_qubits[5]
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (2, 4)]

    def compute_equal(u, v, target):
        lu, hu = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Equal raw two-bit codes.
        qc.cx(lu, lv)
        qc.cx(hu, hv)
        qc.x(lv)
        qc.x(hv)
        qc.mcx([lu, hu, lv, hv], target)
        qc.x(hv)
        qc.x(lv)
        qc.cx(hu, hv)
        qc.cx(lu, lv)

        # The additional equal-color cases: 00 <-> 11.
        qc.cx(lu, hu)
        qc.cx(lv, hv)

        qc.x(hu)
        qc.x(hv)
        qc.x(lv)
        qc.mcx([lu, hu, lv, hv], target)
        qc.x(lv)

        qc.x(lu)
        qc.mcx([lu, hu, lv, hv], target)
        qc.x(lu)

        qc.x(hu)
        qc.x(hv)
        qc.cx(lv, hv)
        qc.cx(lu, hu)

    for (u, v), flag in zip(edges, flags):
        compute_equal(u, v, flag)

    for flag in flags:
        qc.x(flag)

    qc.mcx(flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(flags, phase_ancilla)

    for flag in flags:
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_equal(u, v, flag)
```
