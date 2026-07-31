```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    eq_a, eq_c = ancilla_qubits[:2]

    # A and C decode to 0 iff their two code bits are equal.
    qc.cx(a0, eq_a)
    qc.cx(a1, eq_a)
    qc.cx(c0, eq_c)
    qc.cx(c1, eq_c)

    # Mark: eq_a == 0, b0 == 0, b1 == 1, eq_c == 0.
    qc.x(eq_a)
    qc.x(b0)
    qc.x(eq_c)
    qc.h(eq_c)
    qc.mcx([eq_a, b0, b1], eq_c)
    qc.h(eq_c)
    qc.x(eq_c)
    qc.x(b0)
    qc.x(eq_a)

    # Uncompute equality flags.
    qc.cx(c1, eq_c)
    qc.cx(c0, eq_c)
    qc.cx(a1, eq_a)
    qc.cx(a0, eq_a)
```
