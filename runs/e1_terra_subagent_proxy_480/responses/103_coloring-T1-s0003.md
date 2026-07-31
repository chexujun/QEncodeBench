```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:4]
    target = ancilla_qubits[4]
    def controlled_x(controls, values, target_qubit):
        for qubit, value in zip(controls, values):
            if value == 0: qc.x(qubit)
        qc.mcx(controls, target_qubit)
        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0: qc.x(qubit)
    def edge_equal(a, b, flag):
        a0, a1 = problem_qubits[2*a], problem_qubits[2*a+1]
        b0, b1 = problem_qubits[2*b], problem_qubits[2*b+1]
        controlled_x([a0,a1,b0,b1], [1,0,1,0], flag)
        controlled_x([a0,a1,b0,b1], [0,1,0,1], flag)
        qc.cx(a0,a1); qc.cx(b0,b1); controlled_x([a1,b1], [0,0], flag); qc.cx(b0,b1); qc.cx(a0,a1)
    edges = [(0,2),(0,3),(1,2),(1,3)]
    for (a,b), flag in zip(edges, flags): edge_equal(a,b,flag)
    qc.x(target)
    for flag in flags: qc.x(flag)
    qc.mcx(flags,target)
    for flag in reversed(flags): qc.x(flag)
    for (a,b), flag in reversed(list(zip(edges,flags))): edge_equal(a,b,flag)
```
