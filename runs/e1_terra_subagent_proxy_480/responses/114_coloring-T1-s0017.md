```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def toggle_when(target, controls, values):
        for qubit, value in zip(controls, values):
            if value == 0: qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0: qc.x(qubit)
    def mark_equal(v1, v2, target):
        controls = [problem_qubits[2*v1], problem_qubits[2*v1+1], problem_qubits[2*v2], problem_qubits[2*v2+1]]
        for values in ((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0)):
            toggle_when(target, controls, values)
    edges = ((0,1),(0,2),(1,3))
    flags = ancilla_qubits[:3]
    for (u,v), flag in zip(edges,flags): mark_equal(u,v,flag)
    for flag in flags: qc.x(flag)
    qc.mcp(3.141592653589793, [flags[0],flags[1]], flags[2])
    for flag in reversed(flags): qc.x(flag)
    for (u,v), flag in reversed(list(zip(edges,flags))): mark_equal(u,v,flag)
```
