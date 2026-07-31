```python
def build_oracle(qc):
    edges = ((0, 2), (1, 2), (2, 3), (2, 4), (3, 4))
    flags = [10, 11, 12, 13, 14]
    phase = 15
    def neg_mcx(controls, target):
        for qubit in controls: qc.x(qubit)
        qc.mcx(controls, target)
        for qubit in controls: qc.x(qubit)
    def compute_equal(a, b, target):
        a0, a1 = 2 * a, 2 * a + 1; b0, b1 = 2 * b, 2 * b + 1
        qc.cx(a0, a1); qc.cx(b0, b1); qc.cx(a0, b0); neg_mcx((a1, b1), target)
        qc.x(b0); qc.mcx((a1, b1, b0), target); qc.x(b0)
        qc.cx(a0, b0); qc.cx(b0, b1); qc.cx(a0, a1)
    for (a, b), flag in zip(edges, flags): compute_equal(a, b, flag)
    for flag in flags: qc.x(flag)
    qc.mcx(flags, phase); qc.z(phase); qc.mcx(flags, phase)
    for flag in flags: qc.x(flag)
    for (a, b), flag in reversed(tuple(zip(edges, flags))): compute_equal(a, b, flag)
```
