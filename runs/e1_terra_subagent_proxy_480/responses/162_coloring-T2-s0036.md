```python
def build_oracle(qc, problem_qubits, ancillas):
    edges = [(0, 1), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]

    def toggle_on_pattern(qubits, pattern, target):
        flipped = []
        for qubit, bit in zip(qubits, pattern):
            if bit == 0:
                qc.x(qubit)
                flipped.append(qubit)
        qc.mcx(qubits, target)
        for qubit in reversed(flipped):
            qc.x(qubit)

    def compute_edge_good(u, v, target):
        bits = [problem_qubits[2 * u], problem_qubits[2 * u + 1], problem_qubits[2 * v], problem_qubits[2 * v + 1]]
        equal_patterns = [(0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0)]
        for pattern in equal_patterns:
            toggle_on_pattern(bits, pattern, target)
        qc.x(target)

    for (u, v), target in zip(edges, ancillas[:6]):
        compute_edge_good(u, v, target)
    qc.mcp(3.141592653589793, ancillas[:6])
    for (u, v), target in reversed(list(zip(edges, ancillas[:6]))):
        compute_edge_good(u, v, target)
```
