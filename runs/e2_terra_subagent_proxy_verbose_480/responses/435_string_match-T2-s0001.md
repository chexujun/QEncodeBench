```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s = problem_qubits
    m0, m1, m2, out = ancilla_qubits

    def compute_match(start, target):
        qc.x(s[start + 2])
        qc.x(s[start + 3])
        qc.mcx([s[start + 2], s[start + 3], s[start + 4]], target)
        qc.x(s[start + 3])
        qc.x(s[start + 2])

    def uncompute_match(start, target):
        qc.x(s[start + 2])
        qc.x(s[start + 3])
        qc.mcx([s[start + 2], s[start + 3], s[start + 4]], target)
        qc.x(s[start + 3])
        qc.x(s[start + 2])

    compute_match(0, m0)
    compute_match(1, m1)
    compute_match(2, m2)

    qc.x(out)
    qc.mcx([m0, m1, m2], out, ctrl_state="000")
    qc.z(out)
    qc.mcx([m0, m1, m2], out, ctrl_state="000")
    qc.x(out)

    uncompute_match(2, m2)
    uncompute_match(1, m1)
    uncompute_match(0, m0)
```
