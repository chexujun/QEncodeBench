```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_ancillas = ancilla_qubits[:10]
    count_bits = ancilla_qubits[10:13]  # little-endian 3-bit population count
    c0, c1, c2 = count_bits

    edges = [
        (0, 1), (0, 2), (0, 4), (0, 5), (1, 4),
        (1, 5), (2, 4), (2, 5), (3, 4), (3, 5),
    ]

    # Compute whether each edge is covered: a = x_u OR x_v.
    for (u, v), a in zip(edges, edge_ancillas):
        qc.cx(problem_qubits[u], a)
        qc.cx(problem_qubits[v], a)
        qc.ccx(problem_qubits[u], problem_qubits[v], a)

    # Reversibly accumulate the number of selected vertices.
    for q in problem_qubits:
        qc.ccx(q, c0, c1, c2)
        qc.ccx(q, c0, c1)
        qc.cx(q, c0)

    # A six-bit population count is at most 6, so count <= 3 iff c2 == 0.
    qc.x(c2)
    qc.mcp(math.pi, edge_ancillas, c2)
    qc.x(c2)

    # Uncompute the population count.
    for q in reversed(problem_qubits):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.ccx(q, c0, c1, c2)

    # Uncompute edge-coverage ancillas.
    for (u, v), a in reversed(list(zip(edges, edge_ancillas))):
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.cx(problem_qubits[v], a)
        qc.cx(problem_qubits[u], a)
```
