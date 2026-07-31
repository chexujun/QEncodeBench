```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s=problem_qubits; flag=ancilla_qubits[0]
    qc.x(s[0]);qc.x(s[1]);qc.mcx([s[0],s[1],s[2],s[3]],flag);qc.z(flag);qc.mcx([s[0],s[1],s[2],s[3]],flag);qc.x(s[1]);qc.x(s[0])
    qc.x(s[1]);qc.x(s[2]);qc.mcx([s[1],s[2],s[3],s[4]],flag);qc.z(flag);qc.mcx([s[1],s[2],s[3],s[4]],flag);qc.x(s[2]);qc.x(s[1])
```
