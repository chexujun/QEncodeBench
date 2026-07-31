```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges=((0,1),(0,4),(1,2),(1,3),(1,4),(2,4),(3,4))
    equal_color_patterns=((0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0))
    def toggle_if_equal(v,w,target):
        qubits=(problem_qubits[2*v],problem_qubits[2*v+1],problem_qubits[2*w],problem_qubits[2*w+1])
        for pattern in equal_color_patterns:
            for qubit,value in zip(qubits,pattern):
                if value==0: qc.x(qubit)
            qc.mcx(qubits,target)
            for qubit,value in zip(qubits,pattern):
                if value==0: qc.x(qubit)
    for index,(v,w) in enumerate(edges):
        qc.x(ancilla_qubits[index]); toggle_if_equal(v,w,ancilla_qubits[index])
    qc.x(ancilla_qubits[7]); qc.mcp(3.141592653589793,ancilla_qubits[:7],ancilla_qubits[7]); qc.x(ancilla_qubits[7])
    for index in range(len(edges)-1,-1,-1):
        v,w=edges[index]
        toggle_if_equal(v,w,ancilla_qubits[index]); qc.x(ancilla_qubits[index])
```
