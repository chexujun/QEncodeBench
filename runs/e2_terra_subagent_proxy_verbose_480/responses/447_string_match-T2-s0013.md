```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s = problem_qubits
    m0, m1, m2, flag = ancilla_qubits

    def match(controls, zero_controls, target):
        for q in zero_controls:
            qc.x(q)
        qc.mcx(controls, target)
        for q in reversed(zero_controls):
            qc.x(q)

    # Compute whether each of the three possible offsets matches "11?01".
    match([s[0], s[1], s[3], s[4]], [s[3]], m0)
    match([s[1], s[2], s[4], s[5]], [s[4]], m1)
    match([s[2], s[3], s[5], s[6]], [s[5]], m2)

    # Compute m0 OR m1 OR m2 into flag using its algebraic normal form.
    qc.cx(m0, flag)
    qc.cx(m1, flag)
    qc.cx(m2, flag)
    qc.ccx(m0, m1, flag)
    qc.ccx(m0, m2, flag)
    qc.ccx(m1, m2, flag)
    qc.mcx([m0, m1, m2], flag)

    qc.z(flag)

    # Uncompute the OR flag.
    qc.mcx([m0, m1, m2], flag)
    qc.ccx(m1, m2, flag)
    qc.ccx(m0, m2, flag)
    qc.ccx(m0, m1, flag)
    qc.cx(m2, flag)
    qc.cx(m1, flag)
    qc.cx(m0, flag)

    # Uncompute the individual matches.
    match([s[2], s[3], s[5], s[6]], [s[5]], m2)
    match([s[1], s[2], s[4], s[5]], [s[4]], m1)
    match([s[0], s[1], s[3], s[4]], [s[3]], m0)
```
