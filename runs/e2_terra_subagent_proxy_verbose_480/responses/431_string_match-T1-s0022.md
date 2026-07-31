```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3, _ = problem_qubits
    a0, a1 = ancilla_qubits

    qc.x(q0)
    qc.x(q1)
    qc.x(q2)

    qc.ccx(q0, q1, a0)
    qc.ccx(a0, q2, a1)
    qc.cz(a1, q3)
    qc.ccx(a0, q2, a1)
    qc.ccx(q0, q1, a0)

    qc.x(q2)
    qc.x(q1)
    qc.x(q0)
```
