```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=((0,1),(0,2),(0,3),(0,5),(1,2),(1,3),(1,4),(1,5),(3,5),(4,5)); q=list(problem_qubits)
    for mask in range(64):
        if mask.bit_count()<=4 and all((mask>>u)&1 or (mask>>v)&1 for u,v in edges):
            for i in range(6):
                if not ((mask>>i)&1): qc.x(q[i])
            qc.h(q[0]); qc.mcx(q[1:],q[0]); qc.h(q[0])
            for i in range(6):
                if not ((mask>>i)&1): qc.x(q[i])
```
