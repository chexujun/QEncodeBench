```python
def build_oracle(qc,problem_qubits,ancilla_qubits):
 edges=((0,1),(0,2),(0,4),(1,3),(1,4),(2,4),(3,4),(3,5))
 for m in range(64):
  if m.bit_count()<=4 and all((m>>u)&1 or (m>>v)&1 for u,v in edges):
   for i,q in enumerate(problem_qubits):
    if not ((m>>i)&1): qc.x(q)
   qc.mcp(3.141592653589793,problem_qubits[:-1],problem_qubits[-1])
   for i,q in enumerate(problem_qubits):
    if not ((m>>i)&1): qc.x(q)
```
