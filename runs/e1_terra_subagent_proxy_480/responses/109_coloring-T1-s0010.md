```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    edges = ((0,2),(1,2),(1,3))
    for assignment in range(256):
        colors=[]
        for v in range(4):
            code=(assignment>>(2*v))&3
            colors.append(0 if code==3 else code)
        if all(colors[u] != colors[v] for u,v in edges): qc.mcx(problem_qubits,target,ctrl_state=assignment)
```
