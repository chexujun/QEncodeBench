```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=[(0,4),(1,2),(1,4),(2,3),(2,4)]
    equal_patterns=((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0))
    def toggle_equal_flag(v,w,target):
        controls=[problem_qubits[2*v],problem_qubits[2*v+1],problem_qubits[2*w],problem_qubits[2*w+1]]
        for pattern in equal_patterns:
            for qubit,bit in zip(controls,pattern):
                if bit==0: qc.x(qubit)
            qc.mcx(controls,target)
            for qubit,bit in zip(controls,pattern):
                if bit==0: qc.x(qubit)
    for i,(v,w) in enumerate(edges):
        toggle_equal_flag(v,w,ancilla_qubits[i]); qc.x(ancilla_qubits[i])
    qc.mcx(ancilla_qubits[:5],ancilla_qubits[5]); qc.z(ancilla_qubits[5]); qc.mcx(ancilla_qubits[:5],ancilla_qubits[5])
    for i,(v,w) in reversed(list(enumerate(edges))):
        qc.x(ancilla_qubits[i]); toggle_equal_flag(v,w,ancilla_qubits[i])
```
