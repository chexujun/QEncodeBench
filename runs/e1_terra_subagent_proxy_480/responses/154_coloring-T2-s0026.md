```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (0, 4), (1, 2),
             (1, 3), (1, 4), (2, 3), (3, 4)]
    colors = [0, 1, 2, 0]

    def toggle_for_pattern(controls, pattern, target):
        for qubit, bit in zip(controls, pattern):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in zip(controls, pattern):
            if bit == 0:
                qc.x(qubit)

    def compute_inequality(u, v, target):
        controls = [
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
        ]
        for a in range(4):
            for b in range(4):
                if colors[a] != colors[b]:
                    toggle_for_pattern(
                        controls,
                        [(a >> 1) & 1, a & 1, (b >> 1) & 1, b & 1],
                        target,
                    )

    flags = ancilla_qubits[:8]
    phase = ancilla_qubits[8]

    for (u, v), flag in zip(edges, flags):
        compute_inequality(u, v, flag)

    qc.mcx(flags, phase)
    qc.z(phase)
    qc.mcx(flags, phase)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_inequality(u, v, flag)
```
