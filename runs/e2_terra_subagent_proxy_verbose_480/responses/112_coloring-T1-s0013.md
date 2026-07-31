```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    e01, e03, e12, phase = ancilla_qubits[:4]

    def compute_edge_equal(u, v, target):
        ulo, uhi = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vlo, vhi = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Store each vertex's "nonzero color" flag (low XOR high) in its high bit.
        qc.cx(ulo, uhi)
        qc.cx(vlo, vhi)

        # Both flags zero: both vertices decode to color 0.
        qc.x(uhi)
        qc.x(vhi)
        qc.ccx(uhi, vhi, target)
        qc.x(vhi)
        qc.x(uhi)

        # Both flags one and equal low bits: equal colors 1 or 2.
        qc.cx(ulo, vlo)
        qc.x(vlo)
        qc.mcx([uhi, vhi, vlo], target)
        qc.x(vlo)
        qc.cx(ulo, vlo)

        # Restore problem qubits.
        qc.cx(vlo, vhi)
        qc.cx(ulo, uhi)

    compute_edge_equal(0, 1, e01)
    compute_edge_equal(0, 3, e03)
    compute_edge_equal(1, 2, e12)

    # Put the phase target in |-> and flip it iff no edge is monochromatic.
    qc.x(phase)
    qc.h(phase)
    qc.x(e01)
    qc.x(e03)
    qc.x(e12)
    qc.mcx([e01, e03, e12], phase)
    qc.x(e12)
    qc.x(e03)
    qc.x(e01)
    qc.h(phase)
    qc.x(phase)

    # Uncompute edge-violation flags.
    compute_edge_equal(1, 2, e12)
    compute_edge_equal(0, 3, e03)
    compute_edge_equal(0, 1, e01)
```
