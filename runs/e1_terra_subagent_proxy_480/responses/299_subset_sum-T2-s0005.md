```python
from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    qc.x([q0, q2, q3])
    qc.mcp(pi, [q0, q1, q2], q3)
    qc.x([q0, q2, q3])
```
