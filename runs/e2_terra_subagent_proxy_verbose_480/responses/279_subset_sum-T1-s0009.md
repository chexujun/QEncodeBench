```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    parity, marked = ancilla_qubits[:2]

    qc.cx(x0, parity)
    qc.cx(x1, parity)
    qc.ccx(x2, parity, marked)
    qc.z(marked)
    qc.ccx(x2, parity, marked)
    qc.cx(x1, parity)
    qc.cx(x0, parity)
```
