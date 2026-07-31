```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    a = ancilla_qubits
    def toggle_equal(u, v, target):
        controls = [p[2*u],p[2*u+1],p[2*v],p[2*v+1]]
        for pattern in ((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0)):
            for q,bit in zip(controls,pattern):
                if bit == 0: qc.x(q)
            qc.mcx(controls,target)
            for q,bit in zip(controls,pattern):
                if bit == 0: qc.x(q)
    edges=((0,2),(0,3),(0,4),(1,4))
    for (u,v),target in zip(edges,a[:4]): toggle_equal(u,v,target)
    for q in a[:4]: qc.x(q)
    qc.h(a[4]); qc.mcx(a[:4],a[4]); qc.h(a[4])
    for q in a[:4]: qc.x(q)
    for (u,v),target in reversed(tuple(zip(edges,a[:4]))): toggle_equal(u,v,target)
```
