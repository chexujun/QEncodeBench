```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3 = problem_qubits
    overflow = ancilla_qubits[0]

    # Compute whether at least two of vertices {0, 2, 3} are selected.
    # For three bits, (q0&q2) XOR (q0&q3) XOR (q2&q3) is their majority.
    qc.ccx(q0, q2, overflow)
    qc.ccx(q0, q3, overflow)
    qc.ccx(q2, q3, overflow)

    # Mark iff vertex 1 is selected and the other selected-vertex count is <= 1.
    qc.x(overflow)
    qc.cz(q1, overflow)
    qc.x(overflow)

    # Uncompute the temporary majority/overflow bit.
    qc.ccx(q2, q3, overflow)
    qc.ccx(q0, q3, overflow)
    qc.ccx(q0, q2, overflow)
```
