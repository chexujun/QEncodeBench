```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    flags=ancilla_qubits[:3]; edges=((0,1),(1,3),(2,3)); pairs=((0,0),(0,3),(3,0),(3,3),(1,1),(2,2))
    def eq(u,v,f):
        qs=problem_qubits[2*u:2*u+2]+problem_qubits[2*v:2*v+2]
        for a,b in pairs:
            bits=(a&1,a>>1,b&1,b>>1)
            for q,x in zip(qs,bits):
                if not x: qc.x(q)
            qc.mcx(qs,f)
            for q,x in zip(qs,bits):
                if not x: qc.x(q)
    for (u,v),f in zip(edges,flags): eq(u,v,f)
    for f in flags: qc.x(f)
    qc.mcx(flags,ancilla_qubits[3])
    for f in flags: qc.x(f)
    for (u,v),f in reversed(list(zip(edges,flags))): eq(u,v,f)
```
