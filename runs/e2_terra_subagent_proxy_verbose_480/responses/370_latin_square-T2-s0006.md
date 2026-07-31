```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q = problem_qubits

    # Valid completion requires decoded free-cell values (1, 1, 2),
    # corresponding uniquely to bit pattern (1,0,1,0,0,1).
    for bit in (q[1], q[3], q[4]):
        qc.x(bit)

    qc.h(q[5])
    qc.mcx([q[0], q[1], q[2], q[3], q[4]], q[5])
    qc.h(q[5])

    for bit in (q[4], q[3], q[1]):
        qc.x(bit)
```
