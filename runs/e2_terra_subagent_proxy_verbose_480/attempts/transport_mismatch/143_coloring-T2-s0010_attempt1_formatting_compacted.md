```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    def compute_equal(u, v, target):
        l,h,m,n=problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]
        qc.x(target); qc.cx(l,target); qc.cx(h,target); qc.cx(m,target); qc.cx(n,target)
        qc.ccx(l,n,target); qc.ccx(h,m,target); qc.mcx([l,m,n],target); qc.mcx([h,l,m],target); qc.mcx([h,l,n],target); qc.mcx([h,m,n],target)
    edges=[(0,2),(1,2),(1,3),(1,4),(2,4)]
    for (u,v),flag in zip(edges,flags): compute_equal(u,v,flag)
    for flag in flags: qc.x(flag)
    qc.h(flags[-1]); qc.mcx(flags[:-1],flags[-1]); qc.h(flags[-1])
    for flag in reversed(flags): qc.x(flag)
    for (u,v),flag in reversed(list(zip(edges,flags))): compute_equal(u,v,flag)
```
