```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Match 111110: convert the required 0 at position 5 into a 1-control.
    qc.x(problem_qubits[5])
    qc.mcp(math.pi, problem_qubits[:5], problem_qubits[5])
    qc.x(problem_qubits[5])
```
