```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:7]
    phase = ancilla_qubits[7]
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (2, 4)]

    def toggle_pattern(qubits, bits, target):
        for qubit, bit in zip(qubits, bits):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(qubits, target)
        for qubit, bit in zip(qubits, bits):
            if bit == 0:
                qc.x(qubit)

    def compute_equal(v, w, target):
        a0, a1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        b0, b1 = problem_qubits[2 * w], problem_qubits[2 * w + 1]
        qc.cx(a0, b0)
        qc.cx(a1, b1)
        qc.x(b0)
        qc.x(b1)
        qc.mcx([b0, b1], target)
        qc.x(b0)
        qc.x(b1)
        qc.cx(a1, b1)
        qc.cx(a0, b0)
        toggle_pattern([a0, a1, b0, b1], [0, 0, 1, 1], target)
        toggle_pattern([a0, a1, b0, b1], [1, 1, 0, 0], target)

    for (v, w), flag in zip(edges, flags):
        compute_equal(v, w, flag)
    qc.x(phase)
    qc.h(phase)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, phase)
    for flag in flags:
        qc.x(flag)
    qc.h(phase)
    qc.x(phase)
    for (v, w), flag in reversed(list(zip(edges, flags))):
        compute_equal(v, w, flag)
```
