```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]

    # Cell 0 must decode to 2: code 10.
    qc.x(p[0])
    qc.ccx(p[0], p[1], flags[0])
    qc.x(p[0])

    # Cell 1 must decode to 0: code 00 or 11 (equal bits).
    qc.cx(p[2], flags[1])
    qc.cx(p[3], flags[1])
    qc.x(flags[1])

    # Cell 2 must decode to 1: code 01.
    qc.x(p[5])
    qc.ccx(p[4], p[5], flags[2])
    qc.x(p[5])

    # Cell 3 must decode to 0: code 00 or 11 (equal bits).
    qc.cx(p[6], flags[3])
    qc.cx(p[7], flags[3])
    qc.x(flags[3])

    # Apply a phase exactly when all four cell constraints hold.
    qc.mcx(flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(flags, phase_ancilla)

    # Uncompute the cell predicates.
    qc.x(flags[3])
    qc.cx(p[7], flags[3])
    qc.cx(p[6], flags[3])

    qc.x(p[5])
    qc.ccx(p[4], p[5], flags[2])
    qc.x(p[5])

    qc.x(flags[1])
    qc.cx(p[3], flags[1])
    qc.cx(p[2], flags[1])

    qc.x(p[0])
    qc.ccx(p[0], p[1], flags[0])
    qc.x(p[0])
```
