```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1, d0, d1 = problem_qubits
    eq_a, eq_d = ancilla_qubits[:2]

    # Compute whether cells a and d decode to value 0 (their two bits match).
    qc.x(eq_a)
    qc.cx(a0, eq_a)
    qc.cx(a1, eq_a)

    qc.x(eq_d)
    qc.cx(d0, eq_d)
    qc.cx(d1, eq_d)

    # Required remaining decoded values: b = 1 (01), c = 2 (10).
    qc.x(b1)
    qc.x(c0)

    controls = [eq_a, eq_d, b0, b1, c0, c1]
    qc.mcp(math.pi, controls[:-1], controls[-1])

    qc.x(c0)
    qc.x(b1)

    # Uncompute ancillas.
    qc.cx(d1, eq_d)
    qc.cx(d0, eq_d)
    qc.x(eq_d)

    qc.cx(a1, eq_a)
    qc.cx(a0, eq_a)
    qc.x(eq_a)
```
