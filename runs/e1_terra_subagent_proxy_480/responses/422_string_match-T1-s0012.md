```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s0, _, s2, s3, _ = problem_qubits
    a0 = ancilla_qubits[0]
    qc.x(s0); qc.x(s2); qc.ccx(s0, s2, a0); qc.x(s0); qc.x(s2)
    qc.cz(a0, s3)
    qc.x(s0); qc.x(s2); qc.ccx(s0, s2, a0); qc.x(s0); qc.x(s2)
```
