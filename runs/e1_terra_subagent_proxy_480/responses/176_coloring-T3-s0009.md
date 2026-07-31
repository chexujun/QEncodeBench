```python
def build_oracle(qc,problem_qubits,ancilla_qubits):
    edges=[(0,2),(0,5),(1,2),(1,4),(2,3),(2,4),(3,4),(4,5)]
    def valid_edge(u,v,target):
        a,b=problem_qubits[2*u],problem_qubits[2*u+1];c,d=problem_qubits[2*v],problem_qubits[2*v+1]
        qc.cx(a,b);qc.cx(c,d);qc.x(target);qc.x(b);qc.x(d);qc.mcx([b,d],target);qc.x(d);qc.x(b);qc.x(a);qc.x(c);qc.mcx([a,b,c,d],target);qc.x(c);qc.x(a);qc.mcx([a,b,c,d],target);qc.cx(c,d);qc.cx(a,b)
    work=ancilla_qubits[:5]
    for e,t in zip(edges[:4],work[:4]):valid_edge(*e,t)
    qc.mcx(work[:4],work[4])
    for e,t in reversed(list(zip(edges[:4],work[:4]))):valid_edge(*e,t)
    for e,t in zip(edges[4:],work[:4]):valid_edge(*e,t)
    qc.mcp(3.141592653589793,work[:4],work[4])
    for e,t in reversed(list(zip(edges[4:],work[:4]))):valid_edge(*e,t)
    for e,t in zip(edges[:4],work[:4]):valid_edge(*e,t)
    qc.mcx(work[:4],work[4])
    for e,t in reversed(list(zip(edges[:4],work[:4]))):valid_edge(*e,t)
    return qc
```
