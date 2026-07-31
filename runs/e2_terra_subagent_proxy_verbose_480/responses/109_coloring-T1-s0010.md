```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    e02, e12, e13, work = ancilla_qubits

    def mcx_with_zero_controls(controls, zero_positions, target):
        for i in zero_positions:
            qc.x(controls[i])
        qc.mcx(controls, target)
        for i in reversed(zero_positions):
            qc.x(controls[i])

    def compute_edge_is_valid(vertex_a, vertex_b, target):
        al = problem_qubits[2 * vertex_a]
        ah = problem_qubits[2 * vertex_a + 1]
        bl = problem_qubits[2 * vertex_b]
        bh = problem_qubits[2 * vertex_b + 1]

        # Toggle target iff the decoded colors are equal.
        # Color 0: both low bits are 0; high bits are don't-cares.
        mcx_with_zero_controls([al, bl], [0, 1], target)

        # Color 1: both codes are 01.
        mcx_with_zero_controls([al, ah, bl, bh], [1, 3], target)

        # Color 2: both codes are 10.
        mcx_with_zero_controls([al, ah, bl, bh], [0, 2], target)

        # Convert "equal" to "different".
        qc.x(target)

    compute_edge_is_valid(0, 2, e02)
    compute_edge_is_valid(1, 2, e12)
    compute_edge_is_valid(1, 3, e13)

    qc.mcx([e02, e12, e13], work)
    qc.z(work)
    qc.mcx([e02, e12, e13], work)

    compute_edge_is_valid(1, 3, e13)
    compute_edge_is_valid(1, 2, e12)
    compute_edge_is_valid(0, 2, e02)
```
