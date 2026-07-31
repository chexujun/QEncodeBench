```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def compute_edge_equal(v, w, target):
        a, b = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        c, d = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        # ANF for decoded-color equality:
        # 1+a+b+c+d+ad+bc+acd+abc+bcd+abd
        qc.x(target)
        qc.cx(a, target)
        qc.cx(b, target)
        qc.cx(c, target)
        qc.cx(d, target)
        qc.ccx(a, d, target)
        qc.ccx(b, c, target)
        qc.mcx([a, c, d], target)
        qc.mcx([a, b, c], target)
        qc.mcx([b, c, d], target)
        qc.mcx([a, b, d], target)

    edge_flags = ancilla_qubits[:3]
    phase_ancilla = ancilla_qubits[3]
    edges = [(0, 2), (0, 3), (1, 2)]

    for (v, w), flag in zip(edges, edge_flags):
        compute_edge_equal(v, w, flag)

    # Mark iff no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_flags, phase_ancilla)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (v, w), flag in reversed(list(zip(edges, edge_flags))):
        compute_edge_equal(v, w, flag)
```
