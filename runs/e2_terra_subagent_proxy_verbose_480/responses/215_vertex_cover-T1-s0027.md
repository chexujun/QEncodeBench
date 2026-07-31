```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    v0, v1, v2, v3 = problem_qubits
    invalid = ancilla_qubits[0]

    # invalid = 1 iff at least two of vertices 1, 2, 3 are selected.
    qc.ccx(v1, v2, invalid)
    qc.ccx(v1, v3, invalid)
    qc.ccx(v2, v3, invalid)

    # A valid cover of size <= 2 requires v0 = 1 and invalid = 0.
    qc.x(invalid)
    qc.cz(v0, invalid)
    qc.x(invalid)

    # Uncompute invalid.
    qc.ccx(v2, v3, invalid)
    qc.ccx(v1, v3, invalid)
    qc.ccx(v1, v2, invalid)
```
