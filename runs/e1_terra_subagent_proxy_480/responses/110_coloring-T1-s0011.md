```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edge_ancillas=ancilla_qubits[:3]; target=ancilla_qubits[3]
    def mark(a0,a1,b0,b1,f):
        for vals in ((0,0,0,0),(0,1,0,1),(1,0,1,0),(1,1,1,1)):
            for q,v in zip((a0,a1,b0,b1),vals):
                if not v: qc.x(q)
            qc.mcx([a0,a1,b0,b1],f)
            for q,v in zip((a0,a1,b0,b1),vals):
                if not v: qc.x(q)
    edges=((0,1),(0,2),(0,3))
    for (u,v),f in zip(edges,edge_ancillas): mark(problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1],f)
    for f in edge_ancillas: qc.x(f)
    qc.mcx(edge_ancillas,target)
    for f in edge_ancillas: qc.x(f)
    for (u,v),f in reversed(list(zip(edges,edge_ancillas))): mark(problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1],f)
```
