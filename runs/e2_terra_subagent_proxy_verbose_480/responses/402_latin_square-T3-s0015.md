```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    eq_a, eq_d = ancilla_qubits[:2]

    # Compute whether free cells A=(0,1) and D=(1,2) decode to 0:
    # their two code bits must be equal (00 or 11).
    qc.cx(q[0], eq_a)
    qc.cx(q[1], eq_a)
    qc.x(eq_a)

    qc.cx(q[6], eq_d)
    qc.cx(q[7], eq_d)
    qc.x(eq_d)

    # Required values for B=(0,2) and C=(1,0) are both 1 (code 01).
    qc.x(q[3])
    qc.x(q[5])

    # Phase flip iff:
    # A = 0, B = 1, C = 1, D = 0.
    qc.mcp(math.pi, [eq_a, q[2], q[3], q[4], q[5]], eq_d)

    qc.x(q[5])
    qc.x(q[3])

    # Uncompute equality flags.
    qc.x(eq_d)
    qc.cx(q[7], eq_d)
    qc.cx(q[6], eq_d)

    qc.x(eq_a)
    qc.cx(q[1], eq_a)
    qc.cx(q[0], eq_a)
```
