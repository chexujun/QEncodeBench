```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3 = problem_qubits
    qc.ccz(q0, q1, q3)
    qc.ccz(q0, q2, q3)
```
