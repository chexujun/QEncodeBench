```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q3, q4 = problem_qubits[0], problem_qubits[3], problem_qubits[4]

    qc.x(q4)                    # Convert the required x4 = 0 into a 1-control.
    qc.mcp(math.pi, [q0, q3], q4)
    qc.x(q4)
```
