```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Free-cell codes:
    # a=(1,0) must be 1 -> 01
    # b=(1,1) must decode to 0 -> bits equal
    # c=(2,0) must be 2 -> 10
    # d=(2,2) must decode to 0 -> bits equal
    a0, a1, b0, b1, c0, c1, d0, d1 = problem_qubits
    eq_b, eq_d, flag = ancilla_qubits[:3]

    # Compute whether b and d use either 00 or 11.
    qc.cx(b0, eq_b)
    qc.cx(b1, eq_b)
    qc.x(eq_b)

    qc.cx(d0, eq_d)
    qc.cx(d1, eq_d)
    qc.x(eq_d)

    # Convert required zero-valued literal controls to positive controls.
    qc.x(a1)
    qc.x(c0)

    # Mark iff a=01, c=10, and b,d decode to zero.
    controls = [a0, a1, c0, c1, eq_b, eq_d]
    qc.mcx(controls, flag, mode="noancilla")
    qc.z(flag)
    qc.mcx(controls, flag, mode="noancilla")

    qc.x(c0)
    qc.x(a1)

    # Uncompute equality flags.
    qc.x(eq_d)
    qc.cx(d1, eq_d)
    qc.cx(d0, eq_d)

    qc.x(eq_b)
    qc.cx(b1, eq_b)
    qc.cx(b0, eq_b)
```
