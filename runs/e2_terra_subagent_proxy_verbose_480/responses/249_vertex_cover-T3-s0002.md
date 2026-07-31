```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Eight flags for uncovered edges, then a three-bit counter for
    # the number of vertices omitted from the cover.
    edge_flags = ancilla_qubits[:8]
    count0, count1, count2 = ancilla_qubits[8:11]

    edges = [
        (0, 1), (0, 2), (0, 3), (0, 5),
        (2, 3), (2, 4), (3, 5), (4, 5),
    ]

    # Compute whether each edge is uncovered:
    # flag = (not u) and (not v).
    for flag, (u, v) in zip(edge_flags, edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly count omitted vertices into count0..count2.
    # Each increment is controlled on the corresponding problem bit being 0.
    for vertex in problem_qubits:
        qc.x(vertex)
        qc.mcx([vertex, count0, count1], count2)
        qc.ccx(vertex, count0, count1)
        qc.cx(vertex, count0)
        qc.x(vertex)

    # A valid cover has every edge covered (all flags are zero), and
    # at least two omitted vertices (#ones <= 4).  For counts 0..6,
    # "at least two" is count1 OR count2.
    #
    # Make edge coverage positive controls temporarily.
    for flag in edge_flags:
        qc.x(flag)

    # Apply phase for C AND (count1 OR count2), using
    # OR(a,b) = a + b - ab modulo 2 for phase exponents.
    qc.h(count0)
    qc.mcx(edge_flags + [count1], count0)
    qc.h(count0)

    qc.h(count0)
    qc.mcx(edge_flags + [count2], count0)
    qc.h(count0)

    qc.h(count0)
    qc.mcx(edge_flags + [count1, count2], count0)
    qc.h(count0)

    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute the omitted-vertex counter.
    for vertex in reversed(problem_qubits):
        qc.x(vertex)
        qc.cx(vertex, count0)
        qc.ccx(vertex, count0, count1)
        qc.mcx([vertex, count0, count1], count2)
        qc.x(vertex)

    # Uncompute uncovered-edge flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
