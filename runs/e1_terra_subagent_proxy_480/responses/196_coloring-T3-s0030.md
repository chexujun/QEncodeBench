```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    from qiskit.circuit.library import Diagonal
    edges=((0,1),(0,2),(0,3),(0,4),(1,4),(2,3),(3,4)); diagonal=[]
    for state in range(1<<10):
        colors=[]
        for v in range(5):
            code=(state>>(2*v))&3; colors.append(0 if code==3 else code)
        diagonal.append(-1 if all(colors[u]!=colors[v] for u,v in edges) else 1)
    qc.append(Diagonal(diagonal),problem_qubits)
```
