```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    edge_flags = ancilla_qubits[1:5]
    edges = ((0,1),(0,4),(1,4),(2,3))
    same_color_code_pairs = ((0,0),(0,3),(3,0),(3,3),(1,1),(2,2))
    def toggle_same_color_flag(u,v,flag):
        controls = [problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        for cu,cv in same_color_code_pairs:
            values=(cu&1,cu>>1,cv&1,cv>>1)
            for q,value in zip(controls,values):
                if not value: qc.x(q)
            qc.mcx(controls,flag)
            for q,value in reversed(list(zip(controls,values))):
                if not value: qc.x(q)
    for (u,v),flag in zip(edges,edge_flags): toggle_same_color_flag(u,v,flag)
    for flag in edge_flags: qc.x(flag)
    qc.mcx(edge_flags,target)
    for flag in reversed(edge_flags): qc.x(flag)
    for (u,v),flag in reversed(list(zip(edges,edge_flags))): toggle_same_color_flag(u,v,flag)
```
