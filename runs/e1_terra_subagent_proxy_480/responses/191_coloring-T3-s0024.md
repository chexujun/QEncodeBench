```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from qiskit.circuit.library import DiagonalGate
    edges=((0,4),(0,5),(1,3),(1,5),(2,5),(3,4),(3,5)); diagonal=[]
    for state in range(1<<12):
        colors=[]
        for v in range(6):
            code=((state>>(2*v))&1)|(((state>>(2*v+1))&1)<<1); colors.append(0 if code in (0,3) else code)
        diagonal.append(-1 if all(colors[u]!=colors[v] for u,v in edges) else 1)
    qc.append(DiagonalGate(diagonal),problem_qubits)
```
