```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p0, p1, p2, p3, pair01, pair23 = ancilla_qubits[:6]
    q = problem_qubits

    # Cell 0 decodes to 0 exactly when its two code bits are equal.
    qc.x(p0)
    qc.cx(q[0], p0)
    qc.cx(q[1], p0)

    # Cell 1 decodes to 1 exactly for code 01.
    qc.x(q[3])
    qc.ccx(q[2], q[3], p1)
    qc.x(q[3])

    # Cell 2 decodes to 0 exactly when its two code bits are equal.
    qc.x(p2)
    qc.cx(q[4], p2)
    qc.cx(q[5], p2)

    # Cell 3 decodes to 1 exactly for code 01.
    qc.x(q[7])
    qc.ccx(q[6], q[7], p3)
    qc.x(q[7])

    qc.ccx(p0, p1, pair01)
    qc.ccx(p2, p3, pair23)
    qc.cz(pair01, pair23)
    qc.ccx(p2, p3, pair23)
    qc.ccx(p0, p1, pair01)

    qc.x(q[7])
    qc.ccx(q[6], q[7], p3)
    qc.x(q[7])

    qc.cx(q[5], p2)
    qc.cx(q[4], p2)
    qc.x(p2)

    qc.x(q[3])
    qc.ccx(q[2], q[3], p1)
    qc.x(q[3])

    qc.cx(q[1], p0)
    qc.cx(q[0], p0)
    qc.x(p0)
```
