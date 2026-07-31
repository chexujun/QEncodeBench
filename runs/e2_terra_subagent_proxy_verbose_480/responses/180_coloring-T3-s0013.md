```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Toggles target iff the decoded colors represented by (al, ah) and
    # (bl, bh) are equal.  In particular, 00 and 11 both mean color 0.
    def color_equal(al, ah, bl, bh, target):
        # Put the bitwise code differences in bl and bh.
        qc.cx(al, bl)
        qc.cx(ah, bh)

        # Equal literal codes: bl = bh = 0.
        qc.x(bl)
        qc.x(bh)
        qc.ccx(bl, bh, target)
        qc.x(bh)
        qc.x(bl)

        # The remaining equal-color cases are 00 <-> 11.
        # Here bl = bh = 1 and al == ah.
        qc.cx(al, ah)
        qc.x(ah)
        qc.mcx([bl, bh, ah], target)
        qc.x(ah)
        qc.cx(al, ah)

        # Restore the vertex code bits.
        qc.cx(ah, bh)
        qc.cx(al, bl)

    q = problem_qubits
    a = ancilla_qubits

    # A proper coloring is equivalently:
    # color(0)=color(1), color(2)=color(4), and colors 0,2,3 are distinct.
    color_equal(q[0], q[1], q[2], q[3], a[0])   # 0 == 1
    color_equal(q[4], q[5], q[8], q[9], a[1])   # 2 == 4
    color_equal(q[0], q[1], q[4], q[5], a[2])   # 0 == 2
    color_equal(q[0], q[1], q[6], q[7], a[3])   # 0 == 3
    color_equal(q[4], q[5], q[6], q[7], a[4])   # 2 == 3

    # Apply -1 iff a0=a1=1 and a2=a3=a4=0.
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    qc.h(a[0])
    qc.mcx([a[1], a[2], a[3], a[4]], a[0])
    qc.h(a[0])
    qc.x(a[4])
    qc.x(a[3])
    qc.x(a[2])

    # Uncompute every ancilla.
    color_equal(q[4], q[5], q[6], q[7], a[4])
    color_equal(q[0], q[1], q[6], q[7], a[3])
    color_equal(q[0], q[1], q[4], q[5], a[2])
    color_equal(q[4], q[5], q[8], q[9], a[1])
    color_equal(q[0], q[1], q[2], q[3], a[0])
```
