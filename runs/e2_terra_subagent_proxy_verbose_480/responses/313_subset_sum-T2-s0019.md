```python
from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    predicate = ancilla_qubits[0]

    # sum == 1 iff x0 == 0, x3 == 0, and x1 XOR x2 == 1
    qc.cx(x1, predicate)
    qc.cx(x2, predicate)

    qc.x(x0)
    qc.x(x3)
    qc.mcp(pi, [x0, x3], predicate)
    qc.x(x3)
    qc.x(x0)

    qc.cx(x2, predicate)
    qc.cx(x1, predicate)
```
