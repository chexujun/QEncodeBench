```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits

    # Cell 0 decodes to 0 iff its two code bits are equal.
    qc.x(a[0])
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])

    # Cell 1 must have code 01 (low bit 1, high bit 0).
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])

    # Cell 2 must have code 10 (low bit 0, high bit 1).
    qc.x(q[4])
    qc.ccx(q[4], q[5], a[2])
    qc.x(q[4])

    # Cell 3 decodes to 0 iff its two code bits are equal.
    qc.x(a[3])
    qc.cx(q[6], a[3])
    qc.cx(q[7], a[3])

    # Combine the four conditions into two pairwise conjunctions.
    qc.ccx(a[0], a[1], a[4])
    qc.ccx(a[2], a[3], a[5])

    # Apply -1 exactly when all four conditions hold.
    qc.cz(a[4], a[5])

    # Uncompute pairwise conjunctions.
    qc.ccx(a[2], a[3], a[5])
    qc.ccx(a[0], a[1], a[4])

    # Uncompute cell 3 condition.
    qc.cx(q[7], a[3])
    qc.cx(q[6], a[3])
    qc.x(a[3])

    # Uncompute cell 2 condition.
    qc.x(q[4])
    qc.ccx(q[4], q[5], a[2])
    qc.x(q[4])

    # Uncompute cell 1 condition.
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])

    # Uncompute cell 0 condition.
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
    qc.x(a[0])
```
