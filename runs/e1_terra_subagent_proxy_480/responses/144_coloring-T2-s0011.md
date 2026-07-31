```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags=ancilla_qubits[:5]; phase=ancilla_qubits[5]; edges=[(0,1),(0,4),(1,2),(2,3),(3,4)]
    def mark_equal(u,v,target):
        c=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
        qc.mcx(c,target,ctrl_state="0000"); qc.mcx(c,target,ctrl_state="0101"); qc.mcx(c,target,ctrl_state="1010")
    for (u,v),f in zip(edges,flags): mark_equal(u,v,f)
    qc.x(phase); qc.h(phase); qc.mcx(flags,phase,ctrl_state="00000"); qc.h(phase); qc.x(phase)
    for (u,v),f in reversed(list(zip(edges,flags))): mark_equal(u,v,f)
```
