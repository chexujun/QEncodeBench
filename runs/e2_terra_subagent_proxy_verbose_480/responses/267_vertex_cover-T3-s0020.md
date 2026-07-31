```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    clauses = ancilla_qubits[:7]
    count0, count1, count2 = ancilla_qubits[7:10]

    edges = [(0, 2), (0, 4), (0, 5), (1, 3),
             (2, 5), (3, 5), (4, 5)]

    # Compute each edge's coverage bit: x_u OR x_v.
    for target, (u, v) in zip(clauses, edges):
        qc.cx(problem_qubits[u], target)
        qc.cx(problem_qubits[v], target)
        qc.ccx(problem_qubits[u], problem_qubits[v], target)

    # Reversibly count selected vertices in a three-bit counter.
    for vertex in problem_qubits:
        qc.mcx([vertex, count0, count1], count2)
        qc.ccx(vertex, count0, count1)
        qc.cx(vertex, count0)

    # A cover has size at most three exactly when count2 == 0.
    # Apply a phase iff all seven edge clauses hold and count2 == 0.
    qc.x(count2)
    qc.h(count2)
    qc.mcx(clauses, count2)
    qc.h(count2)
    qc.x(count2)

    # Uncompute the counter.
    for vertex in reversed(problem_qubits):
        qc.cx(vertex, count0)
        qc.ccx(vertex, count0, count1)
        qc.mcx([vertex, count0, count1], count2)

    # Uncompute the edge-coverage bits.
    for target, (u, v) in reversed(list(zip(clauses, edges))):
        qc.ccx(problem_qubits[u], problem_qubits[v], target)
        qc.cx(problem_qubits[v], target)
        qc.cx(problem_qubits[u], target)
```
