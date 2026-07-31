```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:4]
    helper = ancilla_qubits[4]

    edges = ((0, 1), (0, 3), (1, 2), (2, 3))

    def compute_bad_edge(u, v, target):
        lu, hu = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # target = lv XOR hv: 0 exactly when vertex v has color 0.
        qc.cx(lv, target)
        qc.cx(hv, target)

        # helper = lu XOR hu: 0 exactly when vertex u has color 0.
        qc.cx(lu, helper)
        qc.cx(hu, helper)

        # If u is color 0, the edge is bad precisely when v is color 0.
        qc.x(helper)
        qc.cx(helper, target)
        qc.x(helper)

        # If u is nonzero, clear target for the two unequal nonzero-color cases.
        # (u, v) low-bit pairs identify colors 1 and 2 when low XOR high is 1.
        qc.x(lu)
        qc.x(hv)
        qc.mcx([helper, lu, lv, hv], target)
        qc.x(hv)
        qc.x(lu)

        qc.x(lv)
        qc.mcx([helper, lu, lv, hv], target)
        qc.x(lv)

        # Restore the temporary helper.
        qc.cx(hu, helper)
        qc.cx(lu, helper)

    def uncompute_bad_edge(u, v, target):
        lu, hu = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.cx(lu, helper)
        qc.cx(hu, helper)

        qc.x(lv)
        qc.mcx([helper, lu, lv, hv], target)
        qc.x(lv)

        qc.x(lu)
        qc.x(hv)
        qc.mcx([helper, lu, lv, hv], target)
        qc.x(hv)
        qc.x(lu)

        qc.x(helper)
        qc.cx(helper, target)
        qc.x(helper)

        qc.cx(hu, helper)
        qc.cx(lu, helper)

        qc.cx(hv, target)
        qc.cx(lv, target)

    for (u, v), flag in zip(edges, flags):
        compute_bad_edge(u, v, flag)

    # Apply -1 iff every edge flag is zero.
    for flag in flags:
        qc.x(flag)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for flag in flags:
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        uncompute_bad_edge(u, v, flag)
```
