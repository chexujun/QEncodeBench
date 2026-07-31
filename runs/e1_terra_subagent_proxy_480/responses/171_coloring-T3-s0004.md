```python
def build_oracle(qc, q, anc):
    for v in range(5): qc.cx(q[2*v],q[2*v+1])
    def term(target,positive=(),negative=()):
        for qubit in negative: qc.x(qubit)
        qc.mcx(list(positive)+list(negative),target)
        for qubit in reversed(negative): qc.x(qubit)
    def equal_color(v,w,target):
        av,zv=q[2*v],q[2*v+1];aw,zw=q[2*w],q[2*w+1]
        term(target,negative=(zv,zw));term(target,positive=(zv,zw),negative=(av,aw));term(target,positive=(zv,zw,av,aw))
    def distinct_triple(v,w,x,target):
        av,zv=q[2*v],q[2*v+1];aw,zw=q[2*w],q[2*w+1];ax,zx=q[2*x],q[2*x+1]
        term(target,positive=(zw,zx,aw),negative=(zv,ax));term(target,positive=(zw,zx,ax),negative=(zv,aw));term(target,positive=(zv,zx,av),negative=(zw,ax));term(target,positive=(zv,zx,ax),negative=(zw,av));term(target,positive=(zv,zw,av),negative=(zx,aw));term(target,positive=(zv,zw,aw),negative=(zx,av))
    a0,a1,a2,phase=anc[0],anc[1],anc[2],anc[3]
    equal_color(0,3,a0);equal_color(1,2,a1);distinct_triple(2,3,4,a2)
    qc.x(phase);qc.h(phase);qc.mcx([a0,a1,a2],phase);qc.h(phase);qc.x(phase)
    distinct_triple(2,3,4,a2);equal_color(1,2,a1);equal_color(0,3,a0)
    for v in reversed(range(5)): qc.cx(q[2*v],q[2*v+1])
    return qc
```
