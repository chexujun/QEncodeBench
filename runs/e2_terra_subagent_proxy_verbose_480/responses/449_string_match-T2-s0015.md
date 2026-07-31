```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s1, s2, s3, s4 = problem_qubits[1:5]
    m0, m1, m2, out = ancilla_qubits[:4]

    qc.ccx(s1, s2, m0)
    qc.ccx(s2, s3, m1)
    qc.ccx(s3, s4, m2)

    qc.x(m0)
    qc.x(m1)
    qc.x(m2)
    qc.mcx([m0, m1, m2], out)
    qc.x(out)
    qc.x(m2)
    qc.x(m1)
    qc.x(m0)

    qc.z(out)

    qc.x(m0)
    qc.x(m1)
    qc.x(m2)
    qc.x(out)
    qc.mcx([m0, m1, m2], out)
    qc.x(m2)
    qc.x(m1)
    qc.x(m0)

    qc.ccx(s3, s4, m2)
    qc.ccx(s2, s3, m1)
    qc.ccx(s1, s2, m0)
```
