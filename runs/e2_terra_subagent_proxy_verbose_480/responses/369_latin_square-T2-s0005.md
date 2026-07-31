```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Required decoded values: (1, 2, 1), encoded as bits
    # [1,0, 0,1, 1,0].  Flip the zero-valued bit controls.
    zero_bits = [1, 2, 5]
    for i in zero_bits:
        qc.x(problem_qubits[i])

    qc.mcp(math.pi, problem_qubits[:-1], problem_qubits[-1])

    for i in reversed(zero_bits):
        qc.x(problem_qubits[i])
```
