```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    e0, e1, e2, work = ancilla_qubits[:4]

    def toggle_pattern_target(controls, zero_positions, target):
        for index in zero_positions:
            qc.x(controls[index])
        qc.mcx(controls, target, ancilla_qubits=[work], mode="recursion")
        for index in reversed(zero_positions):
            qc.x(controls[index])

    def toggle_equal_color(v, w, target):
        lo_v, hi_v = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        lo_w, hi_w = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        # Equal binary codes.
        qc.cx(lo_v, lo_w)
        qc.cx(hi_v, hi_w)
        qc.x(lo_w)
        qc.x(hi_w)
        qc.ccx(lo_w, hi_w, target)
        qc.x(hi_w)
        qc.x(lo_w)
        qc.cx(hi_v, hi_w)
        qc.cx(lo_v, lo_w)

        # The additional equal-color pairs induced by decoding 00 and 11
        # to the same color.
        controls = [lo_v, hi_v, lo_w, hi_w]
        toggle_pattern_target(controls, [0, 1], target)  # 00, 11
        toggle_pattern_target(controls, [2, 3], target)  # 11, 00

    # Compute which edges are monochromatic.
    toggle_equal_color(0, 2, e0)
    toggle_equal_color(0, 3, e1)
    toggle_equal_color(1, 3, e2)

    # Mark precisely when no edge is monochromatic.
    qc.x(e0)
    qc.x(e1)
    qc.x(e2)
    qc.mcx([e0, e1, e2], work)
    qc.z(work)
    qc.mcx([e0, e1, e2], work)
    qc.x(e2)
    qc.x(e1)
    qc.x(e0)

    # Uncompute all edge predicates.
    toggle_equal_color(1, 3, e2)
    toggle_equal_color(0, 3, e1)
    toggle_equal_color(0, 2, e0)
```
