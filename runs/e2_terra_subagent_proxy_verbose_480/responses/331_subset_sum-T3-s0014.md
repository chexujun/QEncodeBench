```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    p0, p1, p2, p3, p4 = problem_qubits

    # The target 6 can only be formed by selecting the first element (6)
    # and selecting none of the remaining positive elements.
    for qubit in (p1, p2, p3, p4):
        qc.x(qubit)

    qc.mcp(math.pi, [p1, p2, p3, p4], p0)

    for qubit in (p1, p2, p3, p4):
        qc.x(qubit)
```
