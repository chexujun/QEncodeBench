```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 3), (1, 3), (2, 3), (2, 4)]
    flags = ancilla_qubits[:5]
    phase = ancilla_qubits[5]
    equal_pairs = [
        (0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0),
        (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0),
    ]
    def compute_equal(u, v, target):
        controls = [problem_qubits[2*u], problem_qubits[2*u+1], problem_qubits[2*v], problem_qubits[2*v+1]]
        for pattern in equal_pairs:
            for qubit, bit in zip(controls, pattern):
                if bit == 0: qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in zip(controls, pattern):
                if bit == 0: qc.x(qubit)
    for (u, v), flag in zip(edges, flags): compute_equal(u, v, flag)
    qc.x(phase); qc.h(phase); qc.x(flags); qc.mcx(flags, phase); qc.x(flags); qc.h(phase); qc.x(phase)
    for (u, v), flag in reversed(list(zip(edges, flags))): compute_equal(u, v, flag)
```
