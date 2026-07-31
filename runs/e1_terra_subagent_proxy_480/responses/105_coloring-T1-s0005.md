```python
def build_oracle(qc):
 pq=qc.qubits
 def edge_flag(a,b,c,d,target):
  qc.cx(pq[a],pq[c]);qc.cx(pq[b],pq[d]);qc.x(pq[c]);qc.x(pq[d]);qc.mcx([pq[c],pq[d]],pq[target]);qc.x(pq[d]);qc.x(pq[c]);qc.x(pq[a]);qc.x(pq[b]);qc.mcx([pq[c],pq[d],pq[a],pq[b]],pq[target]);qc.x(pq[b]);qc.x(pq[a]);qc.mcx([pq[c],pq[d],pq[a],pq[b]],pq[target]);qc.cx(pq[b],pq[d]);qc.cx(pq[a],pq[c])
 edges=((0,1),(0,3),(2,4),(3,4));flags=(10,11,12,13)
 for (u,v),f in zip(edges,flags):edge_flag(2*u,2*u+1,2*v,2*v+1,f)
 for f in flags:qc.x(pq[f])
 qc.x(pq[14]);qc.h(pq[14]);qc.mcx([pq[10],pq[11],pq[12],pq[13]],pq[14]);qc.h(pq[14]);qc.x(pq[14])
 for f in flags:qc.x(pq[f])
 for (u,v),f in reversed(tuple(zip(edges,flags))):edge_flag(2*u,2*u+1,2*v,2*v+1,f)
```
