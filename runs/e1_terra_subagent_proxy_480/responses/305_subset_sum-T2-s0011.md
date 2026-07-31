```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3 = problem_qubits
    target = ancilla_qubits[0]

    qc.x(q1)
    qc.x(q3)
    qc.mcx([q0, q1, q2, q3], target)
    qc.x(q3)
    qc.x(q1)

    qc.x(q0)
    qc.x(q3)
    qc.mcx([q0, q1, q2, q3], target)
    qc.x(q3)
    qc.x(q0)
```
