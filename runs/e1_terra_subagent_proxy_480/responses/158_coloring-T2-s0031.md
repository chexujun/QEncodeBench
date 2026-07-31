```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    def controlled_x(controls, values, target):
        for qubit, value in zip(controls, values):
            if value == 0: qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0: qc.x(qubit)
    def toggle_different(u, v, target):
        au, bu = problem_qubits[2*u], problem_qubits[2*u+1]
        av, bv = problem_qubits[2*v], problem_qubits[2*v+1]
        qc.x(target)
        controlled_x([au,bu,av,bv], [0,1,0,1], target)
        controlled_x([au,bu,av,bv], [1,0,1,0], target)
        qc.cx(au,bu); qc.cx(av,bv); controlled_x([bu,bv], [0,0], target); qc.cx(av,bv); qc.cx(au,bu)
    edges=[(0,2),(0,4),(1,2),(1,4),(2,3),(2,4)]
    edge_flags=ancilla_qubits[:6]; phase_qubit=ancilla_qubits[6]
    for (u,v),flag in zip(edges,edge_flags): toggle_different(u,v,flag)
    qc.x(phase_qubit); qc.h(phase_qubit); qc.mcx(edge_flags,phase_qubit); qc.h(phase_qubit); qc.x(phase_qubit)
    for (u,v),flag in reversed(list(zip(edges,edge_flags))): toggle_different(u,v,flag)
```
