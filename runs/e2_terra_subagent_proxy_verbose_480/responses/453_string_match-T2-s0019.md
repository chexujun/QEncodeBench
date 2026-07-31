```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a, b, work = ancilla_qubits
    q = problem_qubits

    # Match at offset 0: 101000 on q[0] ... q[5].
    qc.x(q[1])
    qc.x(q[3])
    qc.x(q[4])
    qc.x(q[5])
    qc.mcx([q[0], q[1], q[2], q[3], q[4], q[5]], a,
           ancilla_qubits=[work], mode="recursion")
    qc.x(q[5])
    qc.x(q[4])
    qc.x(q[3])
    qc.x(q[1])

    # Match at offset 1: 101000 on q[1] ... q[6].
    qc.x(q[2])
    qc.x(q[4])
    qc.x(q[5])
    qc.x(q[6])
    qc.mcx([q[1], q[2], q[3], q[4], q[5], q[6]], b,
           ancilla_qubits=[work], mode="recursion")
    qc.x(q[6])
    qc.x(q[5])
    qc.x(q[4])
    qc.x(q[2])

    # Apply phase -1 iff a OR b is true.
    qc.z(a)
    qc.z(b)
    qc.cz(a, b)

    # Uncompute offset 1.
    qc.x(q[2])
    qc.x(q[4])
    qc.x(q[5])
    qc.x(q[6])
    qc.mcx([q[1], q[2], q[3], q[4], q[5], q[6]], b,
           ancilla_qubits=[work], mode="recursion")
    qc.x(q[6])
    qc.x(q[5])
    qc.x(q[4])
    qc.x(q[2])

    # Uncompute offset 0.
    qc.x(q[1])
    qc.x(q[3])
    qc.x(q[4])
    qc.x(q[5])
    qc.mcx([q[0], q[1], q[2], q[3], q[4], q[5]], a,
           ancilla_qubits=[work], mode="recursion")
    qc.x(q[5])
    qc.x(q[4])
    qc.x(q[3])
    qc.x(q[1])
```
