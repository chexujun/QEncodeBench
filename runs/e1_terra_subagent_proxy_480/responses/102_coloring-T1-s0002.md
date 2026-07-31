```python
def build_oracle(qc,pq=None,anc=None):
 pq=list(qc.qubits[:10]) if pq is None else list(pq);anc=list(qc.qubits[10:14]) if anc is None else list(anc)
 def toggle_equal(a0,a1,b0,b1,target):
  controls=[a0,a1,b0,b1];work=[q for q in pq if q not in controls][:2];patterns=((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0))
  for pattern in patterns:
   for q,bit in zip(controls,pattern):
    if bit==0:qc.x(q)
   qc.mcx(controls,target,ancilla_qubits=work,mode='v-chain-dirty')
   for q,bit in reversed(list(zip(controls,pattern))):
    if bit==0:qc.x(q)
 edges=((0,1),(2,3),(3,4))
 for (u,v),f in zip(edges,anc):toggle_equal(pq[2*u],pq[2*u+1],pq[2*v],pq[2*v+1],f)
 for f in anc:qc.x(f)
 qc.h(anc[-1]);qc.mcx(anc[:-1],anc[-1],ancilla_qubits=[pq[0]],mode='v-chain-dirty');qc.h(anc[-1])
 for f in reversed(anc):qc.x(f)
 for (u,v),f in reversed(list(zip(edges,anc))):toggle_equal(pq[2*u],pq[2*u+1],pq[2*v],pq[2*v+1],f)
```
