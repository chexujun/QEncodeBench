```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    count=ancilla_qubits[:4];flag=ancilla_qubits[4];edges=[(0,4),(0,5),(1,3),(1,4),(2,3),(2,5),(3,4),(3,5)]
    def equal_colors(u,v):
        controls=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]];patterns=[(0,0,0,0),(0,0,1,1),(1,1,0,0),(1,1,1,1),(0,1,0,1),(1,0,1,0)]
        for p in patterns:
            for z,b in zip(controls,p):
                if b==0:qc.x(z)
            qc.mcx(controls,flag)
            for z,b in zip(controls,p):
                if b==0:qc.x(z)
    def increment():
        for i in range(3,-1,-1):
            if i==0:qc.cx(flag,count[0])
            else:qc.mcx([flag]+count[:i],count[i])
    def decrement():
        for i in range(4):
            if i==0:qc.cx(flag,count[0])
            else:qc.mcx([flag]+count[:i],count[i])
    for u,v in edges:equal_colors(u,v);increment();equal_colors(u,v)
    for z in count:qc.x(z)
    qc.h(count[3]);qc.mcx(count[:3],count[3]);qc.h(count[3])
    for z in count:qc.x(z)
    for u,v in reversed(edges):equal_colors(u,v);decrement();equal_colors(u,v)
```
