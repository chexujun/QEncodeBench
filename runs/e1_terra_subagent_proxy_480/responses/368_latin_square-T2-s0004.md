```python
from qiskit import QuantumCircuit
import math

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a = ancilla_qubits[0]
    a_low, a_high = problem_qubits[0], problem_qubits[1]
    b_low, b_high = problem_qubits[2], problem_qubits[3]
    c_low, c_high = problem_qubits[4], problem_qubits[5]

    qc.cx(a_low, a)
    qc.cx(a_high, a)
    qc.x(a)
    qc.x(b_low)
    qc.x(c_high)

    qc.mcp(math.pi, [a, b_low, b_high, c_low], c_high)

    qc.x(c_high)
    qc.x(b_low)
    qc.x(a)
    qc.cx(a_high, a)
    qc.cx(a_low, a)
```
