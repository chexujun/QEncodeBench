```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target=ancilla_qubits[0]; edges=((0,1),(0,2),(1,3),(2,3))
    for value in range(256):
        bits=[(value>>i)&1 for i in range(8)]; colors=[(0 if bits[2*v]+2*bits[2*v+1]==3 else bits[2*v]+2*bits[2*v+1]) for v in range(4)]
        if all(colors[u]!=colors[v] for u,v in edges):
            zero=[problem_qubits[i] for i,b in enumerate(bits) if not b]; qc.x(zero); qc.mcx(problem_qubits,target); qc.x(zero)
```
