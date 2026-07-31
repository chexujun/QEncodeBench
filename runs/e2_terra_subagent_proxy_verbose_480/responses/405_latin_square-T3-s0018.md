```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1, c0, c1, d0, d1 = problem_qubits
    phase_target = ancilla_qubits[0]

    # Convert each required condition into an all-ones control condition.
    qc.cx(a1, a0)   # a0 = a0 XOR a1
    qc.x(a0)        # true iff decoded a is 0 (code 00 or 11)

    qc.x(b1)        # b must be code 01
    qc.x(c0)        # c must be code 10

    qc.cx(d1, d0)   # d0 = d0 XOR d1
    qc.x(d0)        # true iff decoded d is 0 (code 00 or 11)

    controls = [a0, a1, b0, b1, c0, c1, d0, d1]

    # Phase kickback: applies -1 exactly when every condition holds.
    qc.h(phase_target)
    qc.mcx(controls, phase_target)
    qc.h(phase_target)

    # Uncompute all temporary condition transformations.
    qc.x(d0)
    qc.cx(d1, d0)

    qc.x(c0)
    qc.x(b1)

    qc.x(a0)
    qc.cx(a1, a0)
```
