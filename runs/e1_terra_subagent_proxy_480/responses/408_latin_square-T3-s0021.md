```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a = ancilla_qubits
    target = a[0]
    work = list(a[1:])

    qc.cx(q[0], q[1])
    qc.cx(q[6], q[7])
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[4])
    qc.x(target)
    qc.h(target)

    qc.mcx([q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7]], target, ancilla_qubits=work, mode="v-chain")

    qc.h(target)
    qc.x(target)
    qc.x(q[4])
    qc.x(q[2])
    qc.x(q[1])
    qc.cx(q[6], q[7])
    qc.cx(q[0], q[1])
```
