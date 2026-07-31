```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits; a = ancilla_qubits
    def edge_diff(v0, v1, target):
        l0,h0=p[2*v0],p[2*v0+1]; l1,h1=p[2*v1],p[2*v1+1]
        qc.x(target)
        qc.cx(l0,h0); qc.cx(l1,h1); qc.x(h0); qc.x(h1); qc.ccx(h0,h1,target); qc.x(h1); qc.x(h0); qc.cx(l1,h1); qc.cx(l0,h0)
        qc.x(h0); qc.x(h1); qc.mcx([l0,h0,l1,h1],target); qc.x(h1); qc.x(h0)
        qc.x(l0); qc.x(l1); qc.mcx([l0,h0,l1,h1],target); qc.x(l1); qc.x(l0)
    edges=[(0,3),(1,2),(1,3),(2,3)]
    for i,(u,v) in enumerate(edges): edge_diff(u,v,a[i])
    qc.mcx(a[:4],a[4]); qc.z(a[4]); qc.mcx(a[:4],a[4])
    for i,(u,v) in reversed(list(enumerate(edges))): edge_diff(u,v,a[i])
```
