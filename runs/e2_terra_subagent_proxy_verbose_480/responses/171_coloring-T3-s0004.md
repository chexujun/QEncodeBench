```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    def compute_color(vertex, color, target):
        low = problem_qubits[2 * vertex]
        high = problem_qubits[2 * vertex + 1]

        if color == 0:
            # color 0 iff low == high (codes 00 and 11)
            qc.x(target)
            qc.cx(low, target)
            qc.cx(high, target)
        elif color == 1:
            # code 01
            qc.x(high)
            qc.ccx(low, high, target)
            qc.x(high)
        else:
            # code 10
            qc.x(low)
            qc.ccx(low, high, target)
            qc.x(low)

    def uncompute_color(vertex, color, target):
        low = problem_qubits[2 * vertex]
        high = problem_qubits[2 * vertex + 1]

        if color == 0:
            qc.cx(high, target)
            qc.cx(low, target)
            qc.x(target)
        elif color == 1:
            qc.x(high)
            qc.ccx(low, high, target)
            qc.x(high)
        else:
            qc.x(low)
            qc.ccx(low, high, target)
            qc.x(low)

    def compute_pair(v_first, v_second, color, target):
        compute_color(v_first, color, a0)
        compute_color(v_second, color, a1)
        qc.ccx(a0, a1, target)
        uncompute_color(v_second, color, a1)
        uncompute_color(v_first, color, a0)

    def uncompute_pair(v_first, v_second, color, target):
        compute_color(v_first, color, a0)
        compute_color(v_second, color, a1)
        qc.ccx(a0, a1, target)
        uncompute_color(v_second, color, a1)
        uncompute_color(v_first, color, a0)

    # A valid coloring has vertices (0,3) sharing one color, vertices
    # (1,2) sharing another, and vertex 4 having the remaining color.
    for color_a in range(3):
        for color_b in range(3):
            if color_b == color_a:
                continue
            color_c = 3 - color_a - color_b

            compute_pair(0, 3, color_a, a2)
            compute_pair(1, 2, color_b, a3)
            compute_color(4, color_c, a0)

            # CCZ(a2, a3, a0)
            qc.h(a0)
            qc.ccx(a2, a3, a0)
            qc.h(a0)

            uncompute_color(4, color_c, a0)
            uncompute_pair(1, 2, color_b, a3)
            uncompute_pair(0, 3, color_a, a2)
```
