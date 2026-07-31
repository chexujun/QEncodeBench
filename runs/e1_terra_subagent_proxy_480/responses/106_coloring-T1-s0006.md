```python
from qiskit import QuantumCircuit
def build_oracle():
    qc=QuantumCircuit(12)
    def compute_bad(a,b,c,d,target):
        qc.cx(b,a);qc.cx(d,c);qc.x(a);qc.x(c);qc.ccx(a,c,target);qc.x(c);qc.x(a);qc.cx(a,b);qc.cx(c,b);qc.cx(d,b);qc.x(b);qc.mcx([a,c,b],target);qc.x(b);qc.cx(d,b);qc.cx(c,b);qc.cx(a,b);qc.cx(d,c);qc.cx(b,a);qc.x(target)
    def uncompute_bad(a,b,c,d,target):
        qc.x(target);qc.cx(b,a);qc.cx(d,c);qc.cx(a,b);qc.cx(c,b);qc.cx(d,b);qc.x(b);qc.mcx([a,c,b],target);qc.x(b);qc.cx(d,b);qc.cx(c,b);qc.cx(a,b);qc.x(a);qc.x(c);qc.ccx(a,c,target);qc.x(c);qc.x(a);qc.cx(d,c);qc.cx(b,a)
    edges=((0,2,8),(1,2,9),(2,3,10),(2,3,11))
    for u,v,f in edges:compute_bad(2*u,2*u+1,2*v,2*v+1,f)
    qc.x([8,9,10,11]);qc.h(8);qc.mcx([9,10,11],8);qc.h(8);qc.x([8,9,10,11])
    for u,v,f in reversed(edges):uncompute_bad(2*u,2*u+1,2*v,2*v+1,f)
    return qc
```
