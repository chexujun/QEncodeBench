```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, b0, b1, c0, c1 = problem_qubits
    equal_c = ancilla_qubits[0]
    flag = ancilla_qubits[1]

    qc.cx(c0, equal_c)
    qc.cx(c1, equal_c)
    qc.x(equal_c)

    qc.x(a1)
    qc.x(b0)
    qc.mcx([a0, a1, b0, b1, equal_c], flag)
    qc.z(flag)
    qc.mcx([a0, a1, b0, b1, equal_c], flag)
    qc.x(b0)
    qc.x(a1)

    qc.x(equal_c)
    qc.cx(c1, equal_c)
    qc.cx(c0, equal_c)
```
