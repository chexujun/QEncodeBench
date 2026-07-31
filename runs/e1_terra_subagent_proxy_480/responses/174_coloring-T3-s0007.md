```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q=problem_qubits;a=ancilla_qubits;edges=[(0,1),(0,2),(0,4),(1,5),(2,3),(2,4),(2,5),(3,5)]
    def inequality(u,v,target):
        x0,x1=q[2*u],q[2*u+1];y0,y1=q[2*v],q[2*v+1];qc.cx(x0,x1);qc.cx(y0,y1);qc.cx(x1,target);qc.cx(y1,target);qc.mcx([x1,y1,x0],target);qc.mcx([x1,y1,y0],target);qc.cx(y0,y1);qc.cx(x0,x1)
    def block(es,flags,out):
        for e,f in zip(es,flags):inequality(e[0],e[1],f)
        qc.mcx(flags,out)
        for e,f in reversed(list(zip(es,flags))):inequality(e[0],e[1],f)
    block(edges[:3],[a[1],a[2],a[3]],a[0]);block(edges[3:6],[a[2],a[3],a[4]],a[1])
    for e,f in zip(edges[6:],[a[2],a[3]]):inequality(e[0],e[1],f)
    qc.h(a[4]);qc.mcx([a[0],a[1],a[2],a[3]],a[4]);qc.h(a[4])
    for e,f in reversed(list(zip(edges[6:],[a[2],a[3]]))):inequality(e[0],e[1],f)
    block(edges[3:6],[a[2],a[3],a[4]],a[1]);block(edges[:3],[a[1],a[2],a[3]],a[0])
```
