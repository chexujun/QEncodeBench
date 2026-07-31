```python
from math import pi
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges=((0,1),(0,3),(0,4),(1,2),(1,3),(2,3),(3,4))
    for state in range(1<<10):
        colors=[]
        for v in range(5):
            low=(state>>(2*v))&1; high=(state>>(2*v+1))&1; colors.append(0 if low and high else low+2*high)
        if all(colors[u]!=colors[v] for u,v in edges):
            zero=[problem_qubits[i] for i in range(10) if not ((state>>i)&1)]
            for q in zero: qc.x(q)
            qc.mcp(pi,problem_qubits[:-1],problem_qubits[-1])
            for q in zero: qc.x(q)
```
