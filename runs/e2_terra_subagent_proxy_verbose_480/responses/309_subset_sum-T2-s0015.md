```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits
    parity, flag = ancilla_qubits[:2]

    # 5*x0 + 9*(x1+x2) + 10*x3 = 24 iff
    # x0 = x3 = 1 and exactly one of x1, x2 is 1.
    qc.cx(x1, parity)
    qc.cx(x2, parity)

    qc.mcx([x0, x3, parity], flag)
    qc.z(flag)
    qc.mcx([x0, x3, parity], flag)

    qc.cx(x2, parity)
    qc.cx(x1, parity)
```
