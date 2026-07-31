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

    # Cell 1 decodes to 1 iff its code is 01: low bit 1, high bit 0.
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])

    # Cells 2 and 3 decode to 0 iff their respective code bits are equal.
    qc.x(a[2])
    qc.cx(q[4], a[2])
    qc.cx(q[5], a[2])

    qc.x(a[3])
    qc.cx(q[6], a[3])
    qc.cx(q[7], a[3])

    # Mark exactly the valid Latin-square completions.
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    qc.z(a[4])
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])

    # Uncompute all predicate ancillas.
    qc.cx(q[7], a[3])
    qc.cx(q[6], a[3])
    qc.x(a[3])

    qc.cx(q[5], a[2])
    qc.cx(q[4], a[2])
    qc.x(a[2])

    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])

    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
    qc.x(a[0])
```
