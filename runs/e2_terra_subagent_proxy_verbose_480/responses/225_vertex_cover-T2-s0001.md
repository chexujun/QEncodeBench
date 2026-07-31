```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    edge_flags = ancilla_qubits[:5]
    size_violation = ancilla_qubits[5]
    predicate = ancilla_qubits[6]

    edges = [(0, 2), (1, 3), (1, 4), (2, 4), (3, 4)]

    # Compute one flag for each uncovered edge.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], flag)
        qc.x(p[v])
        qc.x(p[u])

    # For five bits, XORing all five four-bit conjunctions is 1 exactly
    # when the Hamming weight is 4 or 5.
    four_subsets = [
        [0, 1, 2, 3],
        [0, 1, 2, 4],
        [0, 1, 3, 4],
        [0, 2, 3, 4],
        [1, 2, 3, 4],
    ]
    for subset in four_subsets:
        qc.mcx([p[i] for i in subset], size_violation)

    # Compute the complete predicate: no uncovered edge and no size violation.
    condition_flags = edge_flags + [size_violation]
    for q in condition_flags:
        qc.x(q)
    qc.mcx(condition_flags, predicate)
    for q in reversed(condition_flags):
        qc.x(q)

    qc.z(predicate)

    # Uncompute the predicate.
    for q in condition_flags:
        qc.x(q)
    qc.mcx(condition_flags, predicate)
    for q in reversed(condition_flags):
        qc.x(q)

    # Uncompute the size threshold flag.
    for subset in reversed(four_subsets):
        qc.mcx([p[i] for i in subset], size_violation)

    # Uncompute the uncovered-edge flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], flag)
        qc.x(p[v])
        qc.x(p[u])
```
