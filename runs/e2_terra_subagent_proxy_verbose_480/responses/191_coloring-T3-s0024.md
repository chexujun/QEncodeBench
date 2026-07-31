```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    # The six code-pairs that decode to the same color.  This is decoder
    # logic (not a list of graph-coloring solutions).
    equal_code_pairs = (
        ((0, 0), (0, 0)),
        ((0, 0), (1, 1)),
        ((1, 1), (0, 0)),
        ((1, 1), (1, 1)),
        ((1, 0), (1, 0)),
        ((0, 1), (0, 1)),
    )

    def edge_equal(u, v, target):
        """Toggle target iff the decoded colors at u and v are equal."""
        bits = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]
        for left, right in equal_code_pairs:
            values = (left[0], left[1], right[0], right[1])
            # Use one of the four tested bits as the MCX target.
            controls = bits[:3]
            target_bit = bits[3]
            for bit, value in zip(bits, values):
                if value == 0:
                    qc.x(bit)
            qc.mcx(controls, target_bit)
            qc.cx(target_bit, target)
            qc.mcx(controls, target_bit)
            for bit, value in reversed(tuple(zip(bits, values))):
                if value == 0:
                    qc.x(bit)

    def phase_for_controls(controls, values):
        """Apply -1 exactly when all given qubits have the stated values."""
        target = controls[-1]
        control_bits = controls[:-1]
        for bit, value in zip(controls, values):
            if value == 0:
                qc.x(bit)
        qc.mcp(math.pi, control_bits, target)
        for bit, value in reversed(tuple(zip(controls, values))):
            if value == 0:
                qc.x(bit)

    group_one = ((0, 4), (0, 5), (1, 3))
    group_two = ((1, 5), (2, 5), (3, 4))
    final_edge = (3, 5)

    # Compute validity of the first three edges into a3.
    for edge, flag in zip(group_one, (a0, a1, a2)):
        edge_equal(*edge, flag)
    phase_for_controls((a0, a1, a2, a3), (0, 0, 0, 0))
    qc.x(a3)
    phase_for_controls((a0, a1, a2, a3), (0, 0, 0, 0))
    for edge, flag in reversed(tuple(zip(group_one, (a0, a1, a2)))):
        edge_equal(*edge, flag)

    # a3 is now one iff every edge in group_one is proper.
    for edge, flag in zip(group_two, (a0, a1, a2)):
        edge_equal(*edge, flag)

    # Phase Pbase, where all first six edges are proper.
    phase_for_controls((a3, a0, a1, a2), (1, 0, 0, 0))

    # Since Pbase AND (u != v) = Pbase XOR (Pbase AND (u == v)),
    # add the latter phase for each semantic equality case of the final edge.
    u, v = final_edge
    code_bits = (
        problem_qubits[2 * u],
        problem_qubits[2 * u + 1],
        problem_qubits[2 * v],
        problem_qubits[2 * v + 1],
    )
    for left, right in equal_code_pairs:
        phase_for_controls(
            (a3, a0, a1, a2) + code_bits,
            (1, 0, 0, 0, left[0], left[1], right[0], right[1]),
        )

    # Uncompute all work qubits.
    for edge, flag in reversed(tuple(zip(group_two, (a0, a1, a2)))):
        edge_equal(*edge, flag)

    for edge, flag in zip(group_one, (a0, a1, a2)):
        edge_equal(*edge, flag)
    phase_for_controls((a0, a1, a2, a3), (0, 0, 0, 0))
    qc.x(a3)
    phase_for_controls((a0, a1, a2, a3), (0, 0, 0, 0))
    for edge, flag in reversed(tuple(zip(group_one, (a0, a1, a2)))):
        edge_equal(*edge, flag)
```
