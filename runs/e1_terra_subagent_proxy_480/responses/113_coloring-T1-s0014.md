```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = ((0, 3), (1, 4), (2, 3), (3, 4))
    equal_patterns = ((0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0))
    def toggle_equality(v0, v1, target):
        controls = [problem_qubits[2 * v0], problem_qubits[2 * v0 + 1], problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]]
        for pattern in equal_patterns:
            for qubit, bit in zip(controls, pattern):
                if bit == 0: qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in zip(controls, pattern):
                if bit == 0: qc.x(qubit)
    for (u, v), ancilla in zip(edges, ancilla_qubits[:4]):
        toggle_equality(u, v, ancilla)
    for ancilla in ancilla_qubits[:4]: qc.x(ancilla)
    qc.mcx(ancilla_qubits[:4], ancilla_qubits[4])
    qc.z(ancilla_qubits[4])
    qc.mcx(ancilla_qubits[:4], ancilla_qubits[4])
    for ancilla in ancilla_qubits[:4]: qc.x(ancilla)
    for (u, v), ancilla in reversed(tuple(zip(edges, ancilla_qubits[:4]))):
        toggle_equality(u, v, ancilla)
```
