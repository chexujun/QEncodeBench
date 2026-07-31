```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q = problem_qubits

    # Each free cell must decode to value 1, whose only code is 01.
    # Flip high bits so the desired assignment is all ones.
    for index in (1, 3, 5):
        qc.x(q[index])

    qc.h(q[0])
    qc.mcx([q[1], q[2], q[3], q[4], q[5]], q[0])
    qc.h(q[0])

    for index in (1, 3, 5):
        qc.x(q[index])
```
