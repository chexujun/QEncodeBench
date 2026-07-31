```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_flags = ancilla_qubits[:5]
    work = ancilla_qubits[5]

    def c4x(controls, target):
        qc.ccx(controls[0], controls[1], work)
        qc.mcx([work, controls[2], controls[3]], target)
        qc.ccx(controls[0], controls[1], work)

    def toggle_edge_equal(v, w, target):
        controls = [
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            problem_qubits[2 * w],
            problem_qubits[2 * w + 1],
        ]
        # Codes representing each decoded color.
        color_codes = (
            ((0, 0), (1, 1)),  # color 0
            ((1, 0),),          # color 1
            ((0, 1),),          # color 2
        )

        for codes in color_codes:
            for left in codes:
                for right in codes:
                    bits = left + right
                    for qubit, bit in zip(controls, bits):
                        if bit == 0:
                            qc.x(qubit)
                    c4x(controls, target)
                    for qubit, bit in reversed(list(zip(controls, bits))):
                        if bit == 0:
                            qc.x(qubit)

    edges = ((0, 1), (0, 3), (1, 2), (1, 3), (3, 4))

    for (v, w), flag in zip(edges, edge_flags):
        toggle_edge_equal(v, w, flag)

    for flag in edge_flags:
        qc.x(flag)
    qc.mcp(math.pi, edge_flags[:4], edge_flags[4])
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (v, w), flag in reversed(list(zip(edges, edge_flags))):
        toggle_edge_equal(v, w, flag)
```
