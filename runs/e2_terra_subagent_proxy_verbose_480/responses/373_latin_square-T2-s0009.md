```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    active = ancilla_qubits[0]
    equal_c = ancilla_qubits[1]

    # Compute whether the third free cell decodes to 0:
    # its two code bits must be equal (00 or 11).
    qc.cx(c0, equal_c)
    qc.cx(c1, equal_c)
    qc.x(equal_c)

    # Compute required codes for the first two free cells:
    # cell 0 = 2 -> 10, cell 1 = 1 -> 01.
    qc.x(a0)
    qc.x(b1)
    qc.mcx([a0, a1, b0, b1], active)
    qc.x(b1)
    qc.x(a0)

    # Mark exactly when all three decoded values complete the Latin square.
    qc.cz(active, equal_c)

    # Uncompute.
    qc.x(a0)
    qc.x(b1)
    qc.mcx([a0, a1, b0, b1], active)
    qc.x(b1)
    qc.x(a0)

    qc.x(equal_c)
    qc.cx(c1, equal_c)
    qc.cx(c0, equal_c)
```
