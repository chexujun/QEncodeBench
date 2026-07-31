```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Compute whether each edge is uncovered.
    # An edge (u, v) is uncovered exactly when xu = xv = 0.
    uncovered = ancilla_qubits[:4]
    too_large = ancilla_qubits[4]
    phase = ancilla_qubits[5]

    edges = ((0, 1), (0, 3), (1, 2), (2, 3))

    for (u, v), target in zip(edges, uncovered):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], target)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Compute "Hamming weight >= 3" into too_large.
    # XOR of all 3-way products plus the 4-way product is 1 precisely
    # for weights 3 and 4.
    for triple in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
        qc.mcx([problem_qubits[i] for i in triple], too_large)
    qc.mcx(problem_qubits, too_large)

    # Apply -1 iff every edge is covered and the size is at most 2.
    # Controls are all zero: no uncovered edges and not too_large.
    qc.x(phase)
    qc.h(phase)
    qc.mcx(uncovered + [too_large], phase, ctrl_state=0)
    qc.h(phase)
    qc.x(phase)

    # Uncompute the cardinality predicate.
    qc.mcx(problem_qubits, too_large)
    for triple in reversed(((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))):
        qc.mcx([problem_qubits[i] for i in triple], too_large)

    # Uncompute edge predicates.
    for (u, v), target in reversed(list(zip(edges, uncovered))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], target)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
