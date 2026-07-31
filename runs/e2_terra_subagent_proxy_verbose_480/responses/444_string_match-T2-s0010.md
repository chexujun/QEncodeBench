```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q = problem_qubits

    # Offset 0: s0 s1 s2 s5 = 0 0 1 0
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[5])
    qc.h(q[5])
    qc.mcx([q[0], q[1], q[2]], q[5])
    qc.h(q[5])
    qc.x(q[5])
    qc.x(q[1])
    qc.x(q[0])

    # Offset 1: s1 s2 s3 s6 = 0 0 1 0
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[6])
    qc.h(q[6])
    qc.mcx([q[1], q[2], q[3]], q[6])
    qc.h(q[6])
    qc.x(q[6])
    qc.x(q[2])
    qc.x(q[1])
```
