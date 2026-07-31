```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=[(0,3),(0,5),(1,2),(1,3),(1,4),(1,5),(3,5)]
    for mask in range(64):
        if mask.bit_count()<=4 and all((mask>>u)&1 or (mask>>v)&1 for u,v in edges):
            for i,q in enumerate(problem_qubits):
                if not ((mask>>i)&1): qc.x(q)
            qc.h(problem_qubits[0]); qc.mcx(list(problem_qubits[1:]),problem_qubits[0]); qc.h(problem_qubits[0])
            for i,q in enumerate(problem_qubits):
                if not ((mask>>i)&1): qc.x(q)
```
