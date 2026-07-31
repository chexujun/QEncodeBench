```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    def toggle_pattern(controls, values, target, dirty):
        for qubit, value in zip(controls, values):
            if value == 0:
                qc.x(qubit)
        qc.mcx(controls, target, ancilla_qubits=dirty, mode="v-chain-dirty")
        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0:
                qc.x(qubit)

    def toggle_same_fast(u, v, target, low_work, high_work, dirty):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Equal two-bit codes.
        qc.cx(ul, low_work)
        qc.cx(vl, low_work)
        qc.cx(uh, high_work)
        qc.cx(vh, high_work)
        qc.x(low_work)
        qc.x(high_work)
        qc.ccx(low_work, high_work, target)
        qc.x(high_work)
        qc.x(low_work)
        qc.cx(vh, high_work)
        qc.cx(uh, high_work)
        qc.cx(vl, low_work)
        qc.cx(ul, low_work)

        # The additional two representations of equal decoded color 0.
        controls = [ul, uh, vl, vh]
        toggle_pattern(controls, [0, 0, 1, 1], target, dirty)
        toggle_pattern(controls, [1, 1, 0, 0], target, dirty)

    def toggle_same_direct(u, v, target, dirty):
        controls = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]

        # Equal decoded colors: identical codes, plus 00 <-> 11.
        for values in (
            [0, 0, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 1, 1, 1],
            [0, 0, 1, 1],
            [1, 1, 0, 0],
        ):
            toggle_pattern(controls, values, target, dirty)

    edge_03, edge_13, edge_23, spare = ancilla_qubits

    # Each edge flag is 1 precisely when its endpoint colors differ.
    qc.x(edge_03)
    toggle_same_fast(
        0, 3, edge_03, edge_13, edge_23,
        [problem_qubits[2], problem_qubits[3]],
    )

    qc.x(edge_13)
    toggle_same_fast(
        1, 3, edge_13, edge_23, spare,
        [problem_qubits[0], problem_qubits[1]],
    )

    qc.x(edge_23)
    toggle_same_direct(
        2, 3, edge_23, [problem_qubits[0], problem_qubits[1]]
    )

    qc.mcp(math.pi, [edge_03, edge_13], edge_23)

    toggle_same_direct(
        2, 3, edge_23, [problem_qubits[0], problem_qubits[1]]
    )
    qc.x(edge_23)

    toggle_same_fast(
        1, 3, edge_13, edge_23, spare,
        [problem_qubits[0], problem_qubits[1]],
    )
    qc.x(edge_13)

    toggle_same_fast(
        0, 3, edge_03, edge_13, edge_23,
        [problem_qubits[2], problem_qubits[3]],
    )
    qc.x(edge_03)
```
