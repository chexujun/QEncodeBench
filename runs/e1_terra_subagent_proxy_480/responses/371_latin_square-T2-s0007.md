```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, y0, y1, z0, z1 = problem_qubits
    parity = ancilla_qubits[0]
    phase = ancilla_qubits[1]

    qc.cx(x0, parity)
    qc.cx(x1, parity)

    qc.x(parity)
    qc.x(y1)
    qc.x(z0)

    qc.x(phase)
    qc.h(phase)
    qc.mcx([parity, y0, y1, z0, z1], phase)
    qc.h(phase)
    qc.x(phase)

    qc.x(z0)
    qc.x(y1)
    qc.x(parity)

    qc.cx(x1, parity)
    qc.cx(x0, parity)
```
