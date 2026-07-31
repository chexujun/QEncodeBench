```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    phase = ancilla_qubits[5]
    edges = ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3))
    def edge_difference(v, w, target, inverse=False):
        x0, x1 = problem_qubits[2*v], problem_qubits[2*v+1]
        y0, y1 = problem_qubits[2*w], problem_qubits[2*w+1]
        qc.cx(x1, x0); qc.cx(y1, y0)
        if inverse:
            qc.mcx([x0,y0,y1],target); qc.mcx([x0,y0,x1],target); qc.cx(y0,target); qc.cx(x0,target)
        else:
            qc.cx(x0,target); qc.cx(y0,target); qc.mcx([x0,y0,x1],target); qc.mcx([x0,y0,y1],target)
        qc.cx(y1,y0); qc.cx(x1,x0)
    for edge, flag in zip(edges, flags): edge_difference(*edge, flag)
    qc.x(phase); qc.mcx(flags,phase); qc.z(phase); qc.mcx(flags,phase); qc.x(phase)
    for edge, flag in reversed(list(zip(edges,flags))): edge_difference(*edge,flag,inverse=True)
```
