```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Each free cell must decode to 0, which occurs exactly when its low bit is 0.
    q0 = problem_qubits[0]
    q2 = problem_qubits[2]

    qc.x(q0)
    qc.x(q2)
    qc.cz(q0, q2)
    qc.x(q2)
    qc.x(q0)
```
