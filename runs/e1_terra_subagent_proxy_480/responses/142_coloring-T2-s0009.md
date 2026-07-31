```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def mark_pattern(controls,bits,target):
        for q,b in zip(controls,bits):
            if b==0: qc.x(q)
        qc.mcx(controls,target)
        for q,b in zip(controls,bits):
            if b==0: qc.x(q)
    edges=[(0,2),(0,3),(0,4),(1,4),(3,4)]
    for i,(u,v) in enumerate(edges):
        c=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        mark_pattern(c,[0,0,0,0],ancilla_qubits[i]); mark_pattern(c,[0,1,0,1],ancilla_qubits[i]); mark_pattern(c,[1,0,1,0],ancilla_qubits[i])
    for q in ancilla_qubits[:5]: qc.x(q)
    qc.mcx(ancilla_qubits[:5],ancilla_qubits[5]); qc.z(ancilla_qubits[5]); qc.mcx(ancilla_qubits[:5],ancilla_qubits[5])
    for q in ancilla_qubits[:5]: qc.x(q)
    for i,(u,v) in reversed(list(enumerate(edges))):
        c=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        mark_pattern(c,[1,0,1,0],ancilla_qubits[i]); mark_pattern(c,[0,1,0,1],ancilla_qubits[i]); mark_pattern(c,[0,0,0,0],ancilla_qubits[i])
```
