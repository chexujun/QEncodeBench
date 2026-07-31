```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def toggle_pattern(controls,bits,target):
        for qubit,bit in zip(controls,bits):
            if bit==0: qc.x(qubit)
        qc.mcx(controls,target)
        for qubit,bit in zip(controls,bits):
            if bit==0: qc.x(qubit)
    def color_equal(v1,v2,target):
        controls=[problem_qubits[2*v1],problem_qubits[2*v1+1],problem_qubits[2*v2],problem_qubits[2*v2+1]]
        for bits in ((0,0,0,0),(0,1,0,1),(1,0,1,0),(1,1,1,1),(0,0,1,1),(1,1,0,0)): toggle_pattern(controls,bits,target)
    edges=[(0,1),(0,3),(0,4),(1,2),(1,3),(2,3),(2,4),(3,4)]
    for i,(u,v) in enumerate(edges): color_equal(u,v,ancilla_qubits[i])
    for i in range(8): qc.x(ancilla_qubits[i])
    flag=ancilla_qubits[8]
    qc.mcx(list(ancilla_qubits[:8]),flag); qc.z(flag); qc.mcx(list(ancilla_qubits[:8]),flag)
    for i in range(8): qc.x(ancilla_qubits[i])
    for i,(u,v) in reversed(list(enumerate(edges))): color_equal(u,v,ancilla_qubits[i])
```
