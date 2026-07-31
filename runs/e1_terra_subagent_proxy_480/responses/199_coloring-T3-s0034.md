```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 2), (1, 4), (1, 5), (2, 3), (3, 4), (4, 5))

    diagonal = []
    for state in range(1 << 12):
        colors = []
        for vertex in range(6):
            low = (state >> (2 * vertex)) & 1
            high = (state >> (2 * vertex + 1)) & 1
            colors.append(0 if low == high else (1 if low else 2))
        diagonal.append(-1 if all(colors[u] != colors[v] for u, v in edges) else 1)

    qc.diagonal(diagonal, problem_qubits)
```
