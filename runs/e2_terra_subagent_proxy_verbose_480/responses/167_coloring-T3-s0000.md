```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def xor_minterm(controls, values, target):
        flipped = [q for q, value in zip(controls, values) if value == 0]
        for q in flipped:
            qc.x(q)
        qc.mcx(controls, target)
        for q in reversed(flipped):
            qc.x(q)

    def decoded_equal(a0, a1, b0, b1, target):
        controls = [a0, a1, b0, b1]

        # Both decoded colors are 0: each code is either 00 or 11.
        xor_minterm(controls, [0, 0, 0, 0], target)
        xor_minterm(controls, [0, 0, 1, 1], target)
        xor_minterm(controls, [1, 1, 0, 0], target)
        xor_minterm(controls, [1, 1, 1, 1], target)

        # Both decoded colors are 1 or both are 2.
        xor_minterm(controls, [1, 0, 1, 0], target)
        xor_minterm(controls, [0, 1, 0, 1], target)

    p = problem_qubits
    a = ancilla_qubits

    # The graph is properly colored iff:
    # c0 != c1, c0 != c2, c1 != c2, c3 == c2, and c4 == c0.
    decoded_equal(p[0], p[1], p[2], p[3], a[0])
    decoded_equal(p[0], p[1], p[4], p[5], a[1])
    decoded_equal(p[2], p[3], p[4], p[5], a[2])
    decoded_equal(p[4], p[5], p[6], p[7], a[3])
    decoded_equal(p[0], p[1], p[8], p[9], a[4])

    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])

    qc.h(a[4])
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    qc.h(a[4])

    qc.x(a[2])
    qc.x(a[1])
    qc.x(a[0])

    decoded_equal(p[0], p[1], p[8], p[9], a[4])
    decoded_equal(p[4], p[5], p[6], p[7], a[3])
    decoded_equal(p[2], p[3], p[4], p[5], a[2])
    decoded_equal(p[0], p[1], p[4], p[5], a[1])
    decoded_equal(p[0], p[1], p[2], p[3], a[0])
```
