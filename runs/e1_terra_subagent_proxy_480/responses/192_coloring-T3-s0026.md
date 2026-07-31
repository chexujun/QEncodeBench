```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    diagonal=[]; edges=((0,1),(0,4),(0,5),(1,3),(1,4),(2,3),(2,4),(3,5))
    for state in range(1<<12):
        colors=[]
        for v in range(6):
            a=(state>>(2*v))&1; b=(state>>(2*v+1))&1; colors.append(0 if a==b else (1 if (a,b)==(0,1) else 2))
        diagonal.append(-1 if all(colors[u]!=colors[v] for u,v in edges) else 1)
    qc.diagonal(diagonal,problem_qubits)
```
