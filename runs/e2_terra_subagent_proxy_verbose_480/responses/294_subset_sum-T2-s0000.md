```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3 = problem_qubits
    s0, s1, s2, s3 = ancilla_qubits

    # Compute the four bits of 2*x0 + 7*x1 + x2 + 4*x3.
    qc.cx(x1, s0)
    qc.cx(x2, s0)

    qc.cx(x0, s1)
    qc.cx(x1, s1)
    qc.ccx(x1, x2, s1)

    qc.cx(x1, s2)
    qc.cx(x3, s2)
    qc.ccx(x0, x1, s2)
    qc.ccx(x1, x2, s2)
    qc.mcx([x0, x1, x2], s2)

    qc.ccx(x0, x1, s3)
    qc.ccx(x1, x2, s3)
    qc.ccx(x1, x3, s3)
    qc.mcx([x0, x1, x2], s3)
    qc.mcx([x0, x1, x3], s3)
    qc.mcx([x1, x2, x3], s3)
    qc.mcx([x0, x1, x2, x3], s3)

    # Phase flip iff the sum register equals 12 (binary 1100).
    qc.x(s0)
    qc.x(s1)
    qc.h(s3)
    qc.mcx([s0, s1, s2], s3)
    qc.h(s3)
    qc.x(s1)
    qc.x(s0)

    # Uncompute the sum register.
    qc.mcx([x0, x1, x2, x3], s3)
    qc.mcx([x1, x2, x3], s3)
    qc.mcx([x0, x1, x3], s3)
    qc.mcx([x0, x1, x2], s3)
    qc.ccx(x1, x3, s3)
    qc.ccx(x1, x2, s3)
    qc.ccx(x0, x1, s3)

    qc.mcx([x0, x1, x2], s2)
    qc.ccx(x1, x2, s2)
    qc.ccx(x0, x1, s2)
    qc.cx(x3, s2)
    qc.cx(x1, s2)

    qc.ccx(x1, x2, s1)
    qc.cx(x1, s1)
    qc.cx(x0, s1)

    qc.cx(x2, s0)
    qc.cx(x1, s0)
```
