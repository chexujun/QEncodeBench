```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def mark_different(a, b, c, d, target):
        controls = [a, b, c, d]
        same_color_patterns = ((0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0))
        for pattern in same_color_patterns:
            for qubit, bit in zip(controls, pattern):
                if bit == 0: qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in zip(controls, pattern):
                if bit == 0: qc.x(qubit)
        qc.x(target)
    p = problem_qubits
    a = ancilla_qubits
    mark_different(p[0], p[1], p[2], p[3], a[0])
    mark_different(p[0], p[1], p[6], p[7], a[1])
    mark_different(p[2], p[3], p[4], p[5], a[2])
    qc.h(a[2])
    qc.mcx([a[0], a[1]], a[2])
    qc.h(a[2])
    mark_different(p[2], p[3], p[4], p[5], a[2])
    mark_different(p[0], p[1], p[6], p[7], a[1])
    mark_different(p[0], p[1], p[2], p[3], a[0])
```
