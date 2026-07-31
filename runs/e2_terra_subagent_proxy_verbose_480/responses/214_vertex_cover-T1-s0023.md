```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits
    eq01, eq23, diff02, flag = ancilla_qubits[:4]

    # A size-2 cover is exactly one bipartition of K_{2,2}:
    # x0 == x1, x2 == x3, and x0 != x2.
    qc.cx(x0, eq01)
    qc.cx(x1, eq01)
    qc.cx(x2, eq23)
    qc.cx(x3, eq23)
    qc.cx(x0, diff02)
    qc.cx(x2, diff02)

    qc.x(eq01)
    qc.x(eq23)
    qc.mcx([eq01, eq23, diff02], flag)
    qc.z(flag)
    qc.mcx([eq01, eq23, diff02], flag)
    qc.x(eq23)
    qc.x(eq01)

    qc.cx(x2, diff02)
    qc.cx(x0, diff02)
    qc.cx(x3, eq23)
    qc.cx(x2, eq23)
    qc.cx(x1, eq01)
    qc.cx(x0, eq01)
```
