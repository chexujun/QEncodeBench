```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    eq_a, eq_b, c_is_one = ancilla_qubits[:3]

    qc.cx(a0, eq_a)
    qc.cx(a1, eq_a)
    qc.x(eq_a)

    qc.cx(b0, eq_b)
    qc.cx(b1, eq_b)
    qc.x(eq_b)

    qc.x(c0)
    qc.ccx(c0, c1, c_is_one)
    qc.x(c0)

    qc.h(c_is_one)
    qc.ccx(eq_a, eq_b, c_is_one)
    qc.h(c_is_one)

    qc.x(c0)
    qc.ccx(c0, c1, c_is_one)
    qc.x(c0)

    qc.x(eq_b)
    qc.cx(b1, eq_b)
    qc.cx(b0, eq_b)

    qc.x(eq_a)
    qc.cx(a1, eq_a)
    qc.cx(a0, eq_a)
```
