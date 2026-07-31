```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    eq_02, eq_14, triangle_bad = ancilla_qubits[:3]

    def decoded_equal(v, w, target):
        controls = [
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            problem_qubits[2 * w],
            problem_qubits[2 * w + 1],
        ]
        # The six code-pairs which decode to the same color:
        # color 0: 00/11 paired with 00/11; colors 1 and 2: equal codes.
        for values in ((0, 0, 0, 0), (0, 0, 1, 1),
                       (1, 1, 0, 0), (1, 1, 1, 1),
                       (1, 0, 1, 0), (0, 1, 0, 1)):
            for qubit, value in zip(controls, values):
                if value == 0:
                    qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, value in zip(reversed(controls), reversed(values)):
                if value == 0:
                    qc.x(qubit)

    # For three 3-valued colors, the parity of the three pairwise-equality
    # predicates is 0 exactly when all three colors are distinct.
    decoded_equal(0, 2, eq_02)
    decoded_equal(1, 4, eq_14)
    decoded_equal(0, 1, triangle_bad)
    decoded_equal(0, 3, triangle_bad)
    decoded_equal(1, 3, triangle_bad)

    # Phase iff c2=c0, c4=c1, and the triangle (0,1,3) is properly colored.
    qc.x(triangle_bad)
    qc.mcp(math.pi, [eq_14, triangle_bad], eq_02)
    qc.x(triangle_bad)

    decoded_equal(1, 3, triangle_bad)
    decoded_equal(0, 3, triangle_bad)
    decoded_equal(0, 1, triangle_bad)
    decoded_equal(1, 4, eq_14)
    decoded_equal(0, 2, eq_02)
```
