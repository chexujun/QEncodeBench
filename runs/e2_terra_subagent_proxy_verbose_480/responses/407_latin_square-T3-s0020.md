```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Required decoded values are:
    # cell 0 = 0, cell 1 = 2, cell 2 = 0, cell 3 = 1.
    # A code decodes to 0 exactly when its two bits are equal.
    p = problem_qubits
    eq0, eq2, phase_target = ancilla_qubits[:3]

    # Compute equality tests for cells 0 and 2, then invert so success is |1>.
    qc.cx(p[0], eq0)
    qc.cx(p[1], eq0)
    qc.x(eq0)

    qc.cx(p[4], eq2)
    qc.cx(p[5], eq2)
    qc.x(eq2)

    # Convert required zero-valued literal controls into |1> controls.
    qc.x(p[2])  # cell 1 low bit: 0
    qc.x(p[7])  # cell 3 high bit: 0

    # Phase flip iff all required conditions hold.
    controls = [eq0, p[2], p[3], eq2, p[6], p[7]]
    qc.h(phase_target)
    qc.mcx(controls, phase_target)
    qc.h(phase_target)

    # Restore problem bits and uncompute ancillas.
    qc.x(p[7])
    qc.x(p[2])

    qc.x(eq2)
    qc.cx(p[5], eq2)
    qc.cx(p[4], eq2)

    qc.x(eq0)
    qc.cx(p[1], eq0)
    qc.cx(p[0], eq0)
```
