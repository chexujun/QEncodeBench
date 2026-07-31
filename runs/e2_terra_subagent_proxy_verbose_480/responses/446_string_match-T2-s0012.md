```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s0, s1, _, s3, s4 = problem_qubits
    match0, match1, flag = ancilla_qubits

    # match0 = (~s0) & s3
    qc.x(s0)
    qc.ccx(s0, s3, match0)
    qc.x(s0)

    # match1 = (~s1) & s4
    qc.x(s1)
    qc.ccx(s1, s4, match1)
    qc.x(s1)

    # flag = match0 OR match1
    qc.cx(match0, flag)
    qc.cx(match1, flag)
    qc.ccx(match0, match1, flag)

    qc.z(flag)

    # Uncompute flag
    qc.ccx(match0, match1, flag)
    qc.cx(match1, flag)
    qc.cx(match0, flag)

    # Uncompute matches
    qc.x(s1)
    qc.ccx(s1, s4, match1)
    qc.x(s1)

    qc.x(s0)
    qc.ccx(s0, s3, match0)
    qc.x(s0)
```
