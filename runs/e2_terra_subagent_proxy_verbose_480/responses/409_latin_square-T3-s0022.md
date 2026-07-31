```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    eq0, eq1, phase_target = ancilla_qubits[:3]

    # Cells 0 and 1 decode to 0 precisely when their two code bits agree.
    qc.cx(q[0], eq0)
    qc.cx(q[1], eq0)
    qc.x(eq0)

    qc.cx(q[2], eq1)
    qc.cx(q[3], eq1)
    qc.x(eq1)

    # Required remaining decoded values are cell 2 = 2 (10), cell 3 = 1 (01).
    # Convert their required zero bits into positive controls.
    qc.x(q[5])
    qc.x(q[7])

    # Apply a controlled phase on all six required conditions.
    qc.x(phase_target)
    qc.h(phase_target)
    qc.mcx([eq0, eq1, q[4], q[5], q[6], q[7]], phase_target)
    qc.h(phase_target)
    qc.x(phase_target)

    qc.x(q[7])
    qc.x(q[5])

    # Uncompute equality flags.
    qc.x(eq1)
    qc.cx(q[1], eq1)
    qc.cx(q[0], eq1)

    qc.x(eq0)
    qc.cx(q[3], eq0)
    qc.cx(q[2], eq0)
```
