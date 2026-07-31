```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    eq_a, eq_b, phase_target = ancilla_qubits[:3]

    # Compute whether the first two free-cell codes decode to 0:
    # decoded value 0 iff the two code bits are equal (00 or 11).
    qc.cx(a0, eq_a)
    qc.cx(a1, eq_a)
    qc.x(eq_a)

    qc.cx(b0, eq_b)
    qc.cx(b1, eq_b)
    qc.x(eq_b)

    # The final free cell must decode to 1, whose only code is 01.
    # Turn c1 == 0 into a positive control.
    qc.x(c1)

    # Apply -1 exactly when eq_a = eq_b = c0 = c1_inverted = 1.
    qc.x(phase_target)
    qc.mcp(math.pi, [eq_a, eq_b, c0, c1], phase_target)
    qc.x(phase_target)

    qc.x(c1)

    # Uncompute equality flags.
    qc.x(eq_b)
    qc.cx(b1, eq_b)
    qc.cx(b0, eq_b)

    qc.x(eq_a)
    qc.cx(a1, eq_a)
    qc.cx(a0, eq_a)
```
