```python
def build_oracle(qc,problem_qubits,ancilla_qubits):
 edges=((0,1),(1,4),(1,5),(2,3),(2,5),(3,5))
 for m in range(64):
  if m.bit_count()<=3 and all((m>>u)&1 or (m>>v)&1 for u,v in edges):
   z=[problem_qubits[i] for i in range(6) if not ((m>>i)&1)]; qc.x(z); qc.mcp(3.141592653589793,problem_qubits[:-1],problem_qubits[-1]); qc.x(z)
```
