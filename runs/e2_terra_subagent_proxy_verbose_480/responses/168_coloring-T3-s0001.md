```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # For two encoded colors (a,b) and (c,d), toggle target iff their
    # decoded colors are equal.  The decoding is 00,11 -> 0; 01 -> 1; 10 -> 2.
    def toggle_equal(target, a, b, c, d):
        qc.x(target)
        qc.cx(a, target)
        qc.cx(b, target)
        qc.cx(c, target)
        qc.cx(d, target)
        qc.ccx(a, d, target)
        qc.ccx(b, c, target)
        qc.mcx([a, b, c], target)
        qc.mcx([a, c, d], target)
        qc.mcx([a, b, d], target)
        qc.mcx([b, c, d], target)

    q = problem_qubits
    e01, e04, e14, e03 = ancilla_qubits

    # The graph constraints are equivalently:
    #   0,1,4 are pairwise different; 3 equals 0; and 2 differs from 0.
    toggle_equal(e01, q[0], q[1], q[2], q[3])
    toggle_equal(e04, q[0], q[1], q[8], q[9])
    toggle_equal(e14, q[2], q[3], q[8], q[9])
    toggle_equal(e03, q[0], q[1], q[6], q[7])

    # Convert the first three equality flags into "different" flags.
    qc.x(e01)
    qc.x(e04)
    qc.x(e14)

    # Apply a phase iff e01=e04=e14=e03=1 and color(0) != color(2).
    # The nonconstant ANF terms of "color(0) != color(2)" are used directly.
    shared = [e01, e04, e14]
    a, b, c, d = q[0], q[1], q[4], q[5]

    qc.h(e03)
    qc.mcx(shared + [a], e03)
    qc.mcx(shared + [b], e03)
    qc.mcx(shared + [c], e03)
    qc.mcx(shared + [d], e03)
    qc.mcx(shared + [a, d], e03)
    qc.mcx(shared + [b, c], e03)
    qc.mcx(shared + [a, b, c], e03)
    qc.mcx(shared + [a, c, d], e03)
    qc.mcx(shared + [a, b, d], e03)
    qc.mcx(shared + [b, c, d], e03)
    qc.h(e03)

    qc.x(e14)
    qc.x(e04)
    qc.x(e01)

    toggle_equal(e03, q[0], q[1], q[6], q[7])
    toggle_equal(e14, q[2], q[3], q[8], q[9])
    toggle_equal(e04, q[0], q[1], q[8], q[9])
    toggle_equal(e01, q[0], q[1], q[2], q[3])
```
