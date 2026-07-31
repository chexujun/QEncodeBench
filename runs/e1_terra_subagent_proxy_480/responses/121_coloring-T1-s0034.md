```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target=ancilla_qubits[0]; flags=ancilla_qubits[1:4]; edges=((0,2),(1,2),(3,4)); pairs=((0,0),(0,3),(3,0),(3,3),(1,1),(2,2))
    def eq(u,v,f):
        qs=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        for a,b in pairs:
            bits=(a&1,a>>1,b&1,b>>1)
            for q,x in zip(qs,bits):
                if not x: qc.x(q)
            qc.mcx(qs,f)
            for q,x in zip(qs,bits):
                if not x: qc.x(q)
    for (u,v),f in zip(edges,flags): eq(u,v,f)
    for f in flags: qc.x(f)
    qc.mcx(flags,target)
    for f in flags: qc.x(f)
    for (u,v),f in reversed(list(zip(edges,flags))): eq(u,v,f)
```
