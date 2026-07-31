```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a0, a1, a2, out = ancilla_qubits
    qc.x(q[4]); qc.mcx([q[0], q[1], q[3], q[4]], a0); qc.x(q[4])
    qc.x(q[5]); qc.mcx([q[1], q[2], q[4], q[5]], a1); qc.x(q[5])
    qc.x(q[6]); qc.mcx([q[2], q[3], q[5], q[6]], a2); qc.x(q[6])
    qc.x(a0); qc.x(a1); qc.x(a2); qc.x(out); qc.mcx([a0, a1, a2], out); qc.x(a0); qc.x(a1); qc.x(a2)
    qc.z(out)
    qc.x(a0); qc.x(a1); qc.x(a2); qc.mcx([a0, a1, a2], out); qc.x(out); qc.x(a0); qc.x(a1); qc.x(a2)
    qc.x(q[6]); qc.mcx([q[2], q[3], q[5], q[6]], a2); qc.x(q[6])
    qc.x(q[5]); qc.mcx([q[1], q[2], q[4], q[5]], a1); qc.x(q[5])
    qc.x(q[4]); qc.mcx([q[0], q[1], q[3], q[4]], a0); qc.x(q[4])
```
