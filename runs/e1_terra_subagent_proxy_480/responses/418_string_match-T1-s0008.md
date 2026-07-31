```python
from qiskit import QuantumCircuit
from math import pi

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, _, _, q4, q5 = problem_qubits
    qc.x(q4)
    qc.mcp(pi, [q0, q1, q4], q5)
    qc.x(q4)
```
