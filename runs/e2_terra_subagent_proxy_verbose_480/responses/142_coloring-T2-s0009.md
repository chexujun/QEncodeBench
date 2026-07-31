```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    bad = ancilla_qubits[:5]

    def toggle_equal(u, v, target):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # ANF for decoded-color equality:
        # 1 ⊕ ul ⊕ uh ⊕ vl ⊕ vh
        # ⊕ ul*uh*vl ⊕ ul*uh*vh ⊕ uh*vl
        # ⊕ ul*vl*vh ⊕ ul*vh ⊕ uh*vl*vh
        qc.x(target)
        qc.cx(ul, target)
        qc.cx(uh, target)
        qc.cx(vl, target)
        qc.cx(vh, target)
        qc.ccx(uh, vl, target)
        qc.ccx(ul, vh, target)
        qc.mcx([ul, uh, vl], target)
        qc.mcx([ul, uh, vh], target)
        qc.mcx([ul, vl, vh], target)
        qc.mcx([uh, vl, vh], target)

    edges = [(0, 2), (0, 3), (0, 4), (1, 4), (3, 4)]

    for edge, target in zip(edges, bad):
        toggle_equal(edge[0], edge[1], target)

    for target in bad:
        qc.x(target)
    qc.h(bad[-1])
    qc.mcx(bad[:-1], bad[-1])
    qc.h(bad[-1])
    for target in reversed(bad):
        qc.x(target)

    for edge, target in reversed(list(zip(edges, bad))):
        toggle_equal(edge[0], edge[1], target)
```
