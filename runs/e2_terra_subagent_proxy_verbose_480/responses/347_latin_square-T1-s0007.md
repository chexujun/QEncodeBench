```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    b0, b1, b2, b3 = problem_qubits

    # Validity requires:
    # - first free cell = 2: b0 = 0, b1 = 1
    # - second free cell decodes to 0: b2 == b3 (00 or 11)
    qc.cx(b2, b3)      # b3 now holds b2 XOR b3
    qc.x(b0)
    qc.x(b3)

    # CCZ on b0, b1, b3: phase flips iff all validity conditions hold.
    qc.h(b3)
    qc.ccx(b0, b1, b3)
    qc.h(b3)

    qc.x(b3)
    qc.x(b0)
    qc.cx(b2, b3)      # uncompute equality test
```
