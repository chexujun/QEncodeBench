```python
from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1 = problem_qubits
    parity = ancilla_qubits[0]

    # The square is valid iff cell (0,0) decodes to 1 and cell (1,2)
    # decodes to 0.  The latter is equivalent to its two code bits being equal.
    qc.cx(b0, parity)
    qc.cx(b1, parity)          # parity = b0 XOR b1

    qc.x(a1)                   # require a1 = 0
    qc.x(parity)               # require b0 XOR b1 = 0
    qc.mcp(math.pi, [a0, a1, parity])
    qc.x(parity)
    qc.x(a1)

    qc.cx(b1, parity)
    qc.cx(b0, parity)
```
