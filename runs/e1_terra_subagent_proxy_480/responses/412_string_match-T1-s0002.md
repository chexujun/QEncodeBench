```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q = problem_qubits

    for i in (0, 1, 2, 3, 5):
        qc.x(q[i])

    qc.mcp(3.141592653589793, [q[0], q[1], q[2], q[3], q[4]], q[5])

    for i in (0, 1, 2, 3, 5):
        qc.x(q[i])
```
