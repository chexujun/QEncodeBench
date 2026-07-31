```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    def edge_equal(u, v, target):
        # ANF for equality of decoded colors, XORed into target.
        lo_u, hi_u = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        lo_v, hi_v = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.x(target)
        qc.cx(lo_u, target)
        qc.cx(hi_u, target)
        qc.cx(lo_v, target)
        qc.cx(hi_v, target)
        qc.ccx(hi_u, lo_v, target)
        qc.ccx(lo_u, hi_v, target)
        qc.mcx([hi_u, lo_v, hi_v], target)
        qc.mcx([lo_u, lo_v, hi_v], target)
        qc.mcx([lo_u, hi_u, hi_v], target)
        qc.mcx([lo_u, hi_u, lo_v], target)

    def group_one():
        # Goodness of edges (0,1), (0,2), (0,3), stored in a3.
        edge_equal(0, 1, a0)
        edge_equal(0, 2, a1)
        edge_equal(0, 3, a2)
        qc.x(a0)
        qc.x(a1)
        qc.x(a2)
        qc.mcx([a0, a1, a2], a3)
        qc.x(a2)
        qc.x(a1)
        qc.x(a0)
        edge_equal(0, 3, a2)
        edge_equal(0, 2, a1)
        edge_equal(0, 1, a0)

    def group_two():
        # Goodness of edges (0,4), (1,2), stored in a2.
        edge_equal(0, 4, a0)
        edge_equal(1, 2, a1)
        qc.x(a0)
        qc.x(a1)
        qc.ccx(a0, a1, a2)
        qc.x(a1)
        qc.x(a0)
        edge_equal(1, 2, a1)
        edge_equal(0, 4, a0)

    def group_three():
        # Goodness of edges (2,4), (3,4), stored in a3.
        edge_equal(2, 4, a0)
        edge_equal(3, 4, a2)
        qc.x(a0)
        qc.x(a2)
        qc.ccx(a0, a2, a3)
        qc.x(a2)
        qc.x(a0)
        edge_equal(3, 4, a2)
        edge_equal(2, 4, a0)

    group_one()
    group_two()
    qc.ccx(a3, a2, a1)  # a1 = goodness of first five edges
    group_two()
    group_one()

    group_three()
    qc.cz(a1, a3)
    group_three()

    group_one()
    group_two()
    qc.ccx(a3, a2, a1)
    group_two()
    group_one()
```
