```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    def compute_color_flag(vertex, color, ancilla):
        lo = problem_qubits[2 * vertex]
        hi = problem_qubits[2 * vertex + 1]

        if color == 0:
            qc.cx(lo, ancilla)
            qc.cx(hi, ancilla)
            qc.x(ancilla)
        elif color == 1:
            qc.x(hi)
            qc.ccx(lo, hi, ancilla)
            qc.x(hi)
        else:
            qc.x(lo)
            qc.ccx(lo, hi, ancilla)
            qc.x(lo)

    def uncompute_color_flag(vertex, color, ancilla):
        lo = problem_qubits[2 * vertex]
        hi = problem_qubits[2 * vertex + 1]

        if color == 0:
            qc.x(ancilla)
            qc.cx(hi, ancilla)
            qc.cx(lo, ancilla)
        elif color == 1:
            qc.x(hi)
            qc.ccx(lo, hi, ancilla)
            qc.x(hi)
        else:
            qc.x(lo)
            qc.ccx(lo, hi, ancilla)
            qc.x(lo)

    # Vertices 0, 1, 4 form a triangle.  Once their three colors are
    # distinct, vertices 2, 3, 5 are respectively forced to colors
    # c(1), c(0), c(0).
    color_permutations = (
        (0, 1, 2), (0, 2, 1),
        (1, 0, 2), (1, 2, 0),
        (2, 0, 1), (2, 1, 0),
    )

    for c0, c1, c4 in color_permutations:
        colors = (c0, c1, c1, c0, c4, c0)

        phase_vertex = next(v for v, color in enumerate(colors) if color != 0)
        phase_color = colors[phase_vertex]
        phase_lo = problem_qubits[2 * phase_vertex]
        phase_hi = problem_qubits[2 * phase_vertex + 1]

        if phase_color == 1:
            phase_target = phase_lo
            other_bit = phase_hi
        else:
            phase_target = phase_hi
            other_bit = phase_lo

        flag_data = []
        ancilla_index = 0
        for vertex, color in enumerate(colors):
            if vertex != phase_vertex:
                ancilla = ancilla_qubits[ancilla_index]
                compute_color_flag(vertex, color, ancilla)
                flag_data.append((vertex, color, ancilla))
                ancilla_index += 1

        qc.x(other_bit)
        qc.mcp(math.pi, [ancilla for _, _, ancilla in flag_data] + [other_bit],
               phase_target)
        qc.x(other_bit)

        for vertex, color, ancilla in reversed(flag_data):
            uncompute_color_flag(vertex, color, ancilla)
```
