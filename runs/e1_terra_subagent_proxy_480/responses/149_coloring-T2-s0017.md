```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=[(0,1),(0,3),(1,2),(1,3),(2,3)]
    flags=ancilla_qubits[:5]; work=ancilla_qubits[5]
    def toggle_pattern(bits,values,target):
        zeros=[bits[i] for i,value in enumerate(values) if value==0]
        for qubit in zeros: qc.x(qubit)
        qc.mcx(bits,target)
        for qubit in reversed(zeros): qc.x(qubit)
    patterns=((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0))
    for (u,v),flag in zip(edges,flags):
        bits=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        for pattern in patterns: toggle_pattern(bits,pattern,flag)
    for flag in flags: qc.x(flag)
    qc.mcx(flags,work); qc.z(work); qc.mcx(flags,work)
    for flag in reversed(flags): qc.x(flag)
    for (u,v),flag in reversed(list(zip(edges,flags))):
        bits=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        for pattern in reversed(patterns): toggle_pattern(bits,pattern,flag)
```
