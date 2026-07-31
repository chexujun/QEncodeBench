```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s=problem_qubits; a0,a1,a2,out=ancilla_qubits; flags=(a0,a1,a2)
    for i,flag in enumerate(flags):
        qc.x(s[i+2]);qc.x(s[i+3]);qc.mcx([s[i],s[i+1],s[i+2],s[i+3],s[i+4]],flag);qc.x(s[i+3]);qc.x(s[i+2])
    qc.x(out);qc.x(a0);qc.x(a1);qc.x(a2);qc.mcx([a0,a1,a2],out);qc.x(a2);qc.x(a1);qc.x(a0);qc.z(out)
    qc.x(out);qc.x(a0);qc.x(a1);qc.x(a2);qc.mcx([a0,a1,a2],out);qc.x(a2);qc.x(a1);qc.x(a0);qc.x(out)
    for i,flag in reversed(list(enumerate(flags))):
        qc.x(s[i+2]);qc.x(s[i+3]);qc.mcx([s[i],s[i+1],s[i+2],s[i+3],s[i+4]],flag);qc.x(s[i+3]);qc.x(s[i+2])
```
