```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    count0, count1, count2, equal_flag = ancilla_qubits[:4]

    edges = [(0, 1), (0, 2), (0, 4), (1, 4), (2, 3), (2, 4), (3, 4)]

    def compute_equal(u, v):
        lu, hu = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        controls = [lu, hu, lv, hv]

        # Both decode to color 0: codes 00 and 11 are equivalent.
        for state in ("0000", "0011", "1100", "1111"):
            qc.mcx(controls, equal_flag, ctrl_state=state)

        # Both decode to colors 1 or 2, respectively.
        qc.mcx(controls, equal_flag, ctrl_state="1010")
        qc.mcx(controls, equal_flag, ctrl_state="0101")

    def controlled_increment():
        qc.mcx([equal_flag, count0, count1], count2)
        qc.ccx(equal_flag, count0, count1)
        qc.cx(equal_flag, count0)

    def controlled_decrement():
        qc.cx(equal_flag, count0)
        qc.ccx(equal_flag, count0, count1)
        qc.mcx([equal_flag, count0, count1], count2)

    # Count monochromatic edges modulo 8.  There are only seven edges.
    for u, v in edges:
        compute_equal(u, v)
        controlled_increment()
        compute_equal(u, v)

    # Mark exactly the zero count: all edges have differently colored ends.
    qc.x(count0)
    qc.x(count1)
    qc.x(count2)
    qc.mcp(math.pi, [count0, count1], count2)
    qc.x(count2)
    qc.x(count1)
    qc.x(count0)

    # Uncompute the edge-violation count.
    for u, v in reversed(edges):
        compute_equal(u, v)
        controlled_decrement()
        compute_equal(u, v)
```
