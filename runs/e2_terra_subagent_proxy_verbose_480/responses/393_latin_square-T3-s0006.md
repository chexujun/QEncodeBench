```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits

    # a[0] = 1 iff the first free cell decodes to 0 (code 00 or 11).
    qc.x(a[0])
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])

    # a[1] = 1 iff the second free cell decodes to 0 (code 00 or 11).
    qc.x(a[1])
    qc.cx(q[2], a[1])
    qc.cx(q[3], a[1])

    # The remaining required codes are 10 (value 2) and 01 (value 1).
    qc.x(q[4])
    qc.x(q[7])

    # Phase flip iff all six required conditions hold.
    qc.h(q[7])
    qc.mcx(
        [a[0], a[1], q[4], q[5], q[6]],
        q[7],
        ancilla_qubits=[a[2], a[3], a[4]],
        mode="v-chain",
    )
    qc.h(q[7])

    qc.x(q[7])
    qc.x(q[4])

    # Uncompute the decoded-value predicates.
    qc.cx(q[3], a[1])
    qc.cx(q[2], a[1])
    qc.x(a[1])

    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
    qc.x(a[0])
```
