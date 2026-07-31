```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    def toggle_decoded_equal(v: int, w: int, target: int) -> None:
        \"\"\"XOR target with [decode(v) == decode(w)].\"\"\"
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        wl, wh = problem_qubits[2 * w], problem_qubits[2 * w + 1]
        controls = [vl, vh, wl, wh]

        # The six code pairs that represent equal decoded colors:
        # color 0: 00/11 paired with 00/11; colors 1 and 2: identical codes.
        for bits in ((0, 0, 0, 0), (0, 0, 1, 1),
                     (1, 1, 0, 0), (1, 1, 1, 1),
                     (1, 0, 1, 0), (0, 1, 0, 1)):
            zero_controls = [q for q, bit in zip(controls, bits) if bit == 0]
            for q in zero_controls:
                qc.x(q)
            qc.mcx(controls, target)
            for q in reversed(zero_controls):
                qc.x(q)

    def compute_equal(v: int, w: int, target: int) -> None:
        toggle_decoded_equal(v, w, target)

    def uncompute_equal(v: int, w: int, target: int) -> None:
        toggle_decoded_equal(v, w, target)

    def compute_different(v: int, w: int, target: int) -> None:
        qc.x(target)
        toggle_decoded_equal(v, w, target)

    def uncompute_different(v: int, w: int, target: int) -> None:
        toggle_decoded_equal(v, w, target)
        qc.x(target)

    # A = [c3 = c4], B = [c2 = c0].
    compute_equal(3, 4, a0)
    compute_equal(2, 0, a1)
    qc.ccx(a0, a1, a3)
    uncompute_equal(2, 0, a1)
    uncompute_equal(3, 4, a0)

    # The remaining requirement is that vertices 0, 1, and 4 are all distinct.
    compute_different(0, 1, a2)
    compute_different(0, 4, a0)
    compute_different(1, 4, a1)

    qc.mcp(math.pi, [a3, a2, a0], a1)

    uncompute_different(1, 4, a1)
    uncompute_different(0, 4, a0)
    uncompute_different(0, 1, a2)

    # Clear the stored conjunction.
    compute_equal(3, 4, a0)
    compute_equal(2, 0, a1)
    qc.ccx(a0, a1, a3)
    uncompute_equal(2, 0, a1)
    uncompute_equal(3, 4, a0)
```
