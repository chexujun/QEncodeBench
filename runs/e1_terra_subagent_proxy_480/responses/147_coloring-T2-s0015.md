```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (2, 4)]
    def toggle_on_pattern(controls, pattern, target):
        for qubit, bit in zip(controls, pattern):
            if bit == "0": qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in zip(controls, pattern):
            if bit == "0": qc.x(qubit)
    def compute_edge_equal(u, v, target):
        controls = [problem_qubits[2 * u], problem_qubits[2 * u + 1], problem_qubits[2 * v], problem_qubits[2 * v + 1]]
        for pattern in ("0000", "0011", "1100", "1111", "0101", "1010"):
            toggle_on_pattern(controls, pattern, target)
    for i, (u, v) in enumerate(edges): compute_edge_equal(u, v, ancilla_qubits[i])
    for i in range(6): qc.x(ancilla_qubits[i])
    qc.mcx([ancilla_qubits[i] for i in range(6)], ancilla_qubits[6]); qc.z(ancilla_qubits[6]); qc.mcx([ancilla_qubits[i] for i in range(6)], ancilla_qubits[6])
    for i in range(6): qc.x(ancilla_qubits[i])
    for i in reversed(range(6)):
        u, v = edges[i]
        compute_edge_equal(u, v, ancilla_qubits[i])
```
