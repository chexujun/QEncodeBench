```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_equal(x0: int, x1: int, y0: int, y1: int, target: int) -> None:
        # Both vertices have color 0: b0 == b1 for each vertex.
        qc.cx(x0, x1)
        qc.cx(y0, y1)
        qc.x(x1)
        qc.x(y1)
        qc.ccx(x1, y1, target)
        qc.x(y1)
        qc.x(x1)
        qc.cx(y0, y1)
        qc.cx(x0, x1)

        # Both vertices have color 1: (b0, b1) = (1, 0).
        qc.x(x1)
        qc.x(y1)
        qc.mcx([x0, x1, y0, y1], target)
        qc.x(y1)
        qc.x(x1)

        # Both vertices have color 2: (b0, b1) = (0, 1).
        qc.x(x0)
        qc.x(y0)
        qc.mcx([x0, x1, y0, y1], target)
        qc.x(y0)
        qc.x(x0)

    e02, e03, e13, _ = ancilla_qubits
    q0, q1, q2, q3, q4, q5, q6, q7 = problem_qubits

    toggle_equal(q0, q1, q4, q5, e02)
    toggle_equal(q0, q1, q6, q7, e03)
    toggle_equal(q2, q3, q6, q7, e13)

    qc.x(e02)
    qc.x(e03)
    qc.x(e13)
    qc.ccz(e02, e03, e13)
    qc.x(e13)
    qc.x(e03)
    qc.x(e02)

    toggle_equal(q2, q3, q6, q7, e13)
    toggle_equal(q0, q1, q6, q7, e03)
    toggle_equal(q0, q1, q4, q5, e02)
```
