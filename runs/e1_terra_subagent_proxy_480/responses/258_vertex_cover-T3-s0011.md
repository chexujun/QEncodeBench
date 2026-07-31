```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=[(0,3),(0,4),(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(3,5),(4,5)]; flag=ancilla_qubits[0]
    qc.x(flag); qc.h(flag)
    for mask in range(64):
        if mask.bit_count()<=3 and all((mask>>u)&1 or (mask>>v)&1 for u,v in edges):
            for i in range(6):
                if not ((mask>>i)&1): qc.x(problem_qubits[i])
            qc.mcx(list(problem_qubits),flag)
            for i in range(6):
                if not ((mask>>i)&1): qc.x(problem_qubits[i])
    qc.h(flag); qc.x(flag)
```
