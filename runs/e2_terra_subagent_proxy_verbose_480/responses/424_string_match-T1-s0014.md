```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, _, q2, _ = problem_qubits

    qc.x(q0)
    qc.cz(q0, q2)
    qc.x(q0)
```
