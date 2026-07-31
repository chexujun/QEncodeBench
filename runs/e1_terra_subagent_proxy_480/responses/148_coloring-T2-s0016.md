```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 4), (3, 4)]
    flags = ancilla_qubits[:6]
    work = ancilla_qubits[6]
    def toggle_equal(u, v, target):
        a0, a1 = problem_qubits[2*u], problem_qubits[2*u+1]
        b0, b1 = problem_qubits[2*v], problem_qubits[2*v+1]
        qc.cx(a0,work); qc.cx(a1,work); qc.cx(b0,b1); qc.x(work); qc.x(b1); qc.ccx(work,b1,target); qc.x(b1); qc.x(work); qc.cx(b0,b1); qc.cx(a1,work); qc.cx(a0,work)
        qc.x(a0); qc.x(b0); qc.mcx([a0,a1,b0,b1],target); qc.x(b0); qc.x(a0)
        qc.x(a1); qc.x(b1); qc.mcx([a0,a1,b0,b1],target); qc.x(b1); qc.x(a1)
    for (u,v),flag in zip(edges,flags): toggle_equal(u,v,flag)
    qc.x(flags); qc.h(work); qc.mcx(flags,work); qc.h(work); qc.x(flags)
    for (u,v),flag in zip(reversed(edges),reversed(flags)): toggle_equal(u,v,flag)
```
