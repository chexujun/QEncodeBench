```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    bad = ancilla_qubits[:4]
    scratch = ancilla_qubits[4]

    def compute_bad_edge(v, w, target):
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        lw, hw = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        # target ^= (lv^hv) ^ (lw^hw)
        qc.cx(lv, target)
        qc.cx(hv, target)
        qc.cx(lw, target)
        qc.cx(hw, target)

        # Add (lv^hv) & (lw^hw) & (lv^lw).
        qc.cx(lv, scratch)
        qc.cx(hv, scratch)       # scratch = lv ^ hv
        qc.cx(lw, hw)            # hw = lw ^ hw
        qc.cx(lv, lw)            # lw = lv ^ lw
        qc.mcx([scratch, hw, lw], target)
        qc.cx(lv, lw)
        qc.cx(lw, hw)
        qc.cx(hv, scratch)
        qc.cx(lv, scratch)

    def uncompute_bad_edge(v, w, target):
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        lw, hw = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        qc.cx(lv, scratch)
        qc.cx(hv, scratch)
        qc.cx(lw, hw)
        qc.cx(lv, lw)
        qc.mcx([scratch, hw, lw], target)
        qc.cx(lv, lw)
        qc.cx(lw, hw)
        qc.cx(hv, scratch)
        qc.cx(lv, scratch)

        qc.cx(hw, target)
        qc.cx(lw, target)
        qc.cx(hv, target)
        qc.cx(lv, target)

    edges = [(0, 2), (0, 3), (0, 4), (1, 4)]

    for (v, w), target in zip(edges, bad):
        compute_bad_edge(v, w, target)

    # Mark exactly when no edge is monochromatic.
    for q in bad:
        qc.x(q)
    qc.mcx(bad, scratch)
    qc.z(scratch)
    qc.mcx(bad, scratch)
    for q in reversed(bad):
        qc.x(q)

    for (v, w), target in reversed(list(zip(edges, bad))):
        uncompute_bad_edge(v, w, target)
```
