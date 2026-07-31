```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def toggle_pattern(bits, pattern, target):
        for bit, value in zip(bits, pattern):
            if value == 0: qc.x(bit)
        qc.mcx(bits, target)
        for bit, value in reversed(list(zip(bits, pattern))):
            if value == 0: qc.x(bit)
    def edge_equal(u,v,target):
        bits=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        for p in ((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0)): toggle_pattern(bits,p,target)
    edges=[(0,1),(0,2),(0,3),(1,2),(1,3)]; flags=ancilla_qubits[:5]; work=ancilla_qubits[5]
    for (u,v),flag in zip(edges,flags): edge_equal(u,v,flag)
    for flag in flags: qc.x(flag)
    qc.mcx(flags,work); qc.z(work); qc.mcx(flags,work)
    for flag in flags: qc.x(flag)
    for (u,v),flag in reversed(list(zip(edges,flags))): edge_equal(u,v,flag)
```
