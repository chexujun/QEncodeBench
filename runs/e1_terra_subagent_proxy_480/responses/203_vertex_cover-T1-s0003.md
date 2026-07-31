```python
from qiskit import QuantumCircuit
from math import pi
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    for selected in ((0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)):
        flips = [q for q, bit in zip((q0, q1, q2, q3), selected) if bit == 0]
        qc.x(flips)
        qc.mcp(pi, [q0, q1, q2], q3)
        qc.x(flips)
```
