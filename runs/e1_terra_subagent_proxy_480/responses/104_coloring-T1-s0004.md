```python
def build_oracle(qc,pq):
 flags=list(qc.qubits[8:11])
 def toggle_proper(a,b,c,d,target):
  qc.cx(a,target);qc.cx(b,target);qc.cx(c,target);qc.cx(d,target);qc.ccx(a,d,target);qc.ccx(b,c,target);qc.mcx([a,b,c],target);qc.mcx([a,b,d],target);qc.mcx([a,c,d],target);qc.mcx([b,c,d],target)
 edges=[(0,2),(1,3),(2,3)]
 for t,(u,v) in zip(flags,edges):toggle_proper(pq[2*u],pq[2*u+1],pq[2*v],pq[2*v+1],t)
 qc.h(flags[2]);qc.ccx(flags[0],flags[1],flags[2]);qc.h(flags[2])
 for t,(u,v) in reversed(list(zip(flags,edges))):toggle_proper(pq[2*u],pq[2*u+1],pq[2*v],pq[2*v+1],t)
```
