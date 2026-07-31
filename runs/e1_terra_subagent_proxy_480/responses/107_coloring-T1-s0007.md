```python
from qiskit import QuantumCircuit
def build_oracle():
 qc=QuantumCircuit(10)
 def equal_color(a0,a1,b0,b1,target):
  qc.x(target);qc.cx(a0,target);qc.cx(a1,target);qc.cx(b0,target);qc.cx(b1,target);qc.ccx(a0,b1,target);qc.ccx(a1,b0,target);qc.mcx([a0,a1,b1],target);qc.mcx([a1,b0,b1],target)
 def unequal_color(a0,a1,b0,b1,target):
  qc.mcx([a1,b0,b1],target);qc.mcx([a0,a1,b1],target);qc.ccx(a1,b0,target);qc.ccx(a0,b1,target);qc.cx(b1,target);qc.cx(b0,target);qc.cx(a1,target);qc.cx(a0,target);qc.x(target)
 edges=((0,1,6),(0,2,7),(1,2,8))
 for u,v,f in edges:equal_color(2*u,2*u+1,2*v,2*v+1,f)
 qc.x([6,7,8,9]);qc.h(9);qc.mcx([6,7,8],9);qc.h(9);qc.x([6,7,8,9])
 for u,v,f in reversed(edges):unequal_color(2*u,2*u+1,2*v,2*v+1,f)
 return qc
```
