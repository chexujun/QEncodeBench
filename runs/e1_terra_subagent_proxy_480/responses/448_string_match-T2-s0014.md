```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p=problem_qubits; a0,a1,a2,out=ancilla_qubits
    qc.x(p[1]); qc.mcx([p[0],p[1],p[2]],a0); qc.x(p[1])
    qc.x(p[2]); qc.mcx([p[1],p[2],p[3]],a1); qc.x(p[2])
    qc.x(p[3]); qc.mcx([p[2],p[3],p[4]],a2); qc.x(p[3])
    qc.x(a0); qc.x(a1); qc.x(a2); qc.mcx([a0,a1,a2],out); qc.x(a0); qc.x(a1); qc.x(a2); qc.x(out); qc.z(out); qc.x(out)
    qc.x(a0); qc.x(a1); qc.x(a2); qc.mcx([a0,a1,a2],out); qc.x(a0); qc.x(a1); qc.x(a2)
    qc.x(p[3]); qc.mcx([p[2],p[3],p[4]],a2); qc.x(p[3]); qc.x(p[2]); qc.mcx([p[1],p[2],p[3]],a1); qc.x(p[2]); qc.x(p[1]); qc.mcx([p[0],p[1],p[2]],a0); qc.x(p[1])
```
