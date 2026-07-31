```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_zero_equal(la, ha, lb, hb, target):
        # A code decodes to color 0 exactly when low == high.
        qc.cx(la, ha)
        qc.cx(lb, hb)
        qc.x(ha)
        qc.x(hb)
        qc.mcx([ha, hb], target)
        qc.x(hb)
        qc.x(ha)
        qc.cx(lb, hb)
        qc.cx(la, ha)

    def toggle_one_equal(la, ha, lb, hb, target):
        # Color 1 is encoded by 01.
        qc.x(ha)
        qc.x(hb)
        qc.mcx([la, ha, lb, hb], target)
        qc.x(hb)
        qc.x(ha)

    def toggle_two_equal(la, ha, lb, hb, target):
        # Color 2 is encoded by 10.
        qc.x(la)
        qc.x(lb)
        qc.mcx([la, ha, lb, hb], target)
        qc.x(lb)
        qc.x(la)

    def compute_equal(vertex_a, vertex_b, target):
        la, ha = problem_qubits[2 * vertex_a], problem_qubits[2 * vertex_a + 1]
        lb, hb = problem_qubits[2 * vertex_b], problem_qubits[2 * vertex_b + 1]
        toggle_zero_equal(la, ha, lb, hb, target)
        toggle_one_equal(la, ha, lb, hb, target)
        toggle_two_equal(la, ha, lb, hb, target)

    def uncompute_equal(vertex_a, vertex_b, target):
        la, ha = problem_qubits[2 * vertex_a], problem_qubits[2 * vertex_a + 1]
        lb, hb = problem_qubits[2 * vertex_b], problem_qubits[2 * vertex_b + 1]
        toggle_two_equal(la, ha, lb, hb, target)
        toggle_one_equal(la, ha, lb, hb, target)
        toggle_zero_equal(la, ha, lb, hb, target)

    equal_01, equal_02, equal_13, phase_ancilla = ancilla_qubits[:4]

    compute_equal(0, 1, equal_01)
    compute_equal(0, 2, equal_02)
    compute_equal(1, 3, equal_13)

    # Kick back a minus phase iff no edge is monochromatic.
    qc.x(phase_ancilla)
    qc.h(phase_ancilla)
    qc.mcx([equal_01, equal_02, equal_13], phase_ancilla, ctrl_state=0)
    qc.h(phase_ancilla)
    qc.x(phase_ancilla)

    uncompute_equal(1, 3, equal_13)
    uncompute_equal(0, 2, equal_02)
    uncompute_equal(0, 1, equal_01)
```
