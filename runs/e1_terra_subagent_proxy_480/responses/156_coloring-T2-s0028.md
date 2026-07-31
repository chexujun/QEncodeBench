```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from math import pi

    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (2, 4), (3, 4)]
    equal_patterns = [
        (0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0),
        (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0),
    ]

    def compute_equal(v, w, target):
        controls = [
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
            problem_qubits[2 * w], problem_qubits[2 * w + 1],
        ]
        for pattern in equal_patterns:
            for qubit, bit in zip(controls, pattern):
                if bit == 0:
                    qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in zip(controls, pattern):
                if bit == 0:
                    qc.x(qubit)

    for edge, ancilla in zip(edges, ancilla_qubits):
        compute_equal(edge[0], edge[1], ancilla)

    for ancilla in ancilla_qubits[:6]:
        qc.x(ancilla)
    qc.mcp(pi, ancilla_qubits[:5], ancilla_qubits[5])
    for ancilla in ancilla_qubits[:6]:
        qc.x(ancilla)

    for edge, ancilla in reversed(list(zip(edges, ancilla_qubits))):
        compute_equal(edge[0], edge[1], ancilla)
```
