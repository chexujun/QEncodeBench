```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    f01, f23, f34, scratch = ancilla_qubits

    def toggle_when(controls, values, target):
        zero_controls = [q for q, value in zip(controls, values) if value == 0]
        for q in zero_controls:
            qc.x(q)
        qc.mcx(controls, target)
        for q in reversed(zero_controls):
            qc.x(q)

    def compute_edge_valid(v, w, target):
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        wl, wh = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        # scratch = vl XOR wl
        qc.cx(vl, scratch)
        qc.cx(wl, scratch)

        # Toggle target iff the decoded colors are equal.
        patterns = [
            ([scratch, vh, wh], [0, 0, 0]),  # identical codes with high bit 0
            ([scratch, vh, wh], [0, 1, 1]),  # identical codes with high bit 1
            ([scratch, vl, vh], [1, 0, 0]),  # 00 versus 11
            ([scratch, vl, vh], [1, 1, 1]),  # 11 versus 00
        ]
        for controls, values in patterns:
            toggle_when(controls, values, target)

        qc.x(target)  # target now means "edge colors differ"

    def uncompute_edge_valid(v, w, target):
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        wl, wh = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        qc.x(target)
        patterns = [
            ([scratch, vh, wh], [0, 0, 0]),
            ([scratch, vh, wh], [0, 1, 1]),
            ([scratch, vl, vh], [1, 0, 0]),
            ([scratch, vl, vh], [1, 1, 1]),
        ]
        for controls, values in reversed(patterns):
            toggle_when(controls, values, target)

        qc.cx(wl, scratch)
        qc.cx(vl, scratch)

    compute_edge_valid(0, 1, f01)
    compute_edge_valid(2, 3, f23)
    compute_edge_valid(3, 4, f34)

    qc.h(f34)
    qc.ccx(f01, f23, f34)
    qc.h(f34)

    uncompute_edge_valid(3, 4, f34)
    uncompute_edge_valid(2, 3, f23)
    uncompute_edge_valid(0, 1, f01)
```
