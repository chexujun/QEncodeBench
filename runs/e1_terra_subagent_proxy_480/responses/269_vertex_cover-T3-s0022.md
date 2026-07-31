```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=[(0,1),(0,4),(0,5),(1,2),(1,3),(3,5)]
    for mask in range(64):
        if mask.bit_count() <= 3 and all(((mask>>u)&1) or ((mask>>v)&1) for u,v in edges):
            for i,q in enumerate(problem_qubits):
                if not ((mask>>i)&1): qc.x(q)
            qc.mcp(3.141592653589793,problem_qubits[:-1],problem_qubits[-1])
            for i,q in enumerate(problem_qubits):
                if not ((mask>>i)&1): qc.x(q)
```
