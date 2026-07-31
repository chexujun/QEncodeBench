```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = ((0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (3, 4))
    diagonal = []

    for state in range(1 << 12):
        colors = []
        for vertex in range(6):
            code = ((state >> (2 * vertex)) & 1) + 2 * ((state >> (2 * vertex + 1)) & 1)
            colors.append(0 if code == 3 else code)

        valid = all(colors[u] != colors[v] for u, v in edges)
        diagonal.append(-1 if valid else 1)

    qc.diagonal(diagonal, problem_qubits)
```
