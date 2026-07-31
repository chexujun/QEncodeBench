```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The three possible occurrences are mutually exclusive, so applying
    # one phase flip per matching offset implements their logical OR.
    for offset in range(3):
        window = problem_qubits[offset:offset + 5]

        # Convert required zeroes in pattern 01110 into one-controls.
        qc.x(window[0])
        qc.x(window[4])

        qc.mcp(math.pi, window[:4], window[4])

        qc.x(window[4])
        qc.x(window[0])
```
