```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]

    # Cell 0 decodes to 0 iff its two code bits are equal.
    qc.x(flags[0])
    qc.cx(p[0], flags[0])
    qc.cx(p[1], flags[0])

    # Cell 1 decodes to 1 iff (b0, b1) = (1, 0).
    qc.x(p[3])
    qc.ccx(p[2], p[3], flags[1])
    qc.x(p[3])

    # Cell 2 decodes to 1 iff (b0, b1) = (1, 0).
    qc.x(p[5])
    qc.ccx(p[4], p[5], flags[2])
    qc.x(p[5])

    # Cell 3 decodes to 0 iff its two code bits are equal.
    qc.x(flags[3])
    qc.cx(p[6], flags[3])
    qc.cx(p[7], flags[3])

    # Apply the phase exactly when all four required cell values hold.
    qc.mcx(flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(flags, phase_ancilla)

    # Uncompute all predicate flags.
    qc.cx(p[7], flags[3])
    qc.cx(p[6], flags[3])
    qc.x(flags[3])

    qc.x(p[5])
    qc.ccx(p[4], p[5], flags[2])
    qc.x(p[5])

    qc.x(p[3])
    qc.ccx(p[2], p[3], flags[1])
    qc.x(p[3])

    qc.cx(p[1], flags[0])
    qc.cx(p[0], flags[0])
    qc.x(flags[0])
```
