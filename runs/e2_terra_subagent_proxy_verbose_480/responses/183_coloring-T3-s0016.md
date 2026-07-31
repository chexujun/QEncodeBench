```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # The graph constraints imply:
    #   c0 != c2,
    #   c1 = c3 = the third color distinct from c0 and c2,
    #   c4 != c1.
    #
    # For each possible ordered pair (c0, c2), compute the four required
    # color predicates into ancillas, phase the matching states, then cancel
    # the phase when c4 has the forbidden color.

    def compute_is_color(qubit_pair, color, target):
        low, high = qubit_pair
        if color == 0:
            qc.x(target)
            qc.cx(low, target)          # target = not low
        elif color == 1:
            qc.x(high)
            qc.ccx(low, high, target)   # low=1, high=0
            qc.x(high)
        else:
            qc.x(low)
            qc.ccx(low, high, target)   # low=0, high=1
            qc.x(low)

    def uncompute_is_color(qubit_pair, color, target):
        low, high = qubit_pair
        if color == 0:
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

    vertices = [
        problem_qubits[0:2],
        problem_qubits[2:4],
        problem_qubits[4:6],
        problem_qubits[6:8],
        problem_qubits[8:10],
    ]
    a0, a1, a2, a3 = ancilla_qubits

    for color0 in range(3):
        for color2 in range(3):
            if color0 == color2:
                continue

            third = 3 - color0 - color2

            compute_is_color(vertices[0], color0, a0)
            compute_is_color(vertices[2], color2, a1)
            compute_is_color(vertices[1], third, a2)
            compute_is_color(vertices[3], third, a3)

            flags = [a0, a1, a2, a3]

            # Phase when c0,c2,c1,c3 satisfy the required relationship.
            qc.mcp(math.pi, flags[:-1], flags[-1])

            # Cancel that phase precisely when c4 equals the third color.
            low4, high4 = vertices[4]
            if third == 0:
                qc.x(low4)
                qc.mcp(math.pi, flags, low4)
                qc.x(low4)
            elif third == 1:
                qc.x(high4)
                qc.mcp(math.pi, flags + [low4], high4)
                qc.x(high4)
            else:
                qc.x(low4)
                qc.mcp(math.pi, flags + [low4], high4)
                qc.x(low4)

            uncompute_is_color(vertices[3], third, a3)
            uncompute_is_color(vertices[1], third, a2)
            uncompute_is_color(vertices[2], color2, a1)
            uncompute_is_color(vertices[0], color0, a0)
```
