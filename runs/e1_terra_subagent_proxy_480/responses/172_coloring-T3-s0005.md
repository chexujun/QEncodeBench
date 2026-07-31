```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q=problem_qubits;a0,a1,a2,a3=ancilla_qubits
    edges_a=((0,1),(1,2),(1,3));edges_b=((1,5),(2,4),(2,5));eq=((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0))
    def toggle(controls,target,pat):
        z=[x for x,v in zip(controls,pat) if v==0]
        for x in z:qc.x(x)
        qc.mcx(controls,target)
        for x in reversed(z):qc.x(x)
    def comp(edge,target):
        u,v=edge;c=(q[2*u],q[2*u+1],q[2*v],q[2*v+1])
        for p in eq:toggle(c,target,p)
        qc.x(target)
    def uncomp(edge,target):
        qc.x(target);u,v=edge;c=(q[2*u],q[2*u+1],q[2*v],q[2*v+1])
        for p in reversed(eq):toggle(c,target,p)
    for e,t in zip(edges_a,(a0,a1,a2)):comp(e,t)
    qc.ccx(a0,a1,a3);qc.ccx(a3,a2,a3);qc.ccx(a0,a1,a3)
    for e,t in zip(reversed(edges_a),(a2,a1,a0)):uncomp(e,t)
    for e,t in zip(edges_b,(a0,a1,a2)):comp(e,t)
    qc.h(a2);qc.mcx((a3,a0,a1),a2);qc.h(a2)
    for e,t in zip(reversed(edges_b),(a2,a1,a0)):uncomp(e,t)
    for e,t in zip(edges_a,(a0,a1,a2)):comp(e,t)
    qc.ccx(a0,a1,a3);qc.ccx(a3,a2,a3);qc.ccx(a0,a1,a3)
    for e,t in zip(reversed(edges_a),(a2,a1,a0)):uncomp(e,t)
```
