```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a = ancilla_qubits[0]
    controls = problem_qubits[:3]

    for q in controls:
        qc.x(q)

    qc.x(a)
    qc.h(a)
    qc.mcx(controls, a)
    qc.h(a)
    qc.x(a)

    for q in reversed(controls):
        qc.x(q)
```
