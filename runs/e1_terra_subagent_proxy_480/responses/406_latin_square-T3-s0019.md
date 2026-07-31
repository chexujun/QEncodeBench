```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    zero_controls = [p[1], p[2], p[3], p[5], p[6], p[7]]
    for q in zero_controls: qc.x(q)
    qc.h(p[0])
    qc.mcx([p[1],p[2],p[3],p[4],p[5],p[6],p[7]], p[0], ancilla_qubits=ancilla_qubits, mode="v-chain")
    qc.h(p[0])
    for q in reversed(zero_controls): qc.x(q)
```
