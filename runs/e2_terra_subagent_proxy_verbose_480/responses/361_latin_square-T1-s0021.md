```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, b0, b1 = problem_qubits
    flag = ancilla_qubits[0]

    # flag = a0 XOR a1; equality means decoded first cell is 0.
    qc.cx(a0, flag)
    qc.cx(a1, flag)

    # Convert required conditions to all-ones:
    # flag == 0 (first cell decodes to 0), b0 == 1, b1 == 0.
    qc.x(flag)
    qc.x(b1)

    # CCZ(flag, b1, b0), implemented as H-CCX-H.
    qc.h(b0)
    qc.ccx(flag, b1, b0)
    qc.h(b0)

    qc.x(b1)
    qc.x(flag)

    # Uncompute flag.
    qc.cx(a1, flag)
    qc.cx(a0, flag)
```
