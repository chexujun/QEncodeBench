```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # A three-bit counter stores the number of monochromatic edges (0..7).
    # The remaining ancilla is a temporary edge-equality flag.
    count = ancilla_qubits[:3]
    flag = ancilla_qubits[3]

    edges = ((0, 1), (0, 3), (0, 4), (1, 3), (1, 5), (2, 5), (4, 5))

    def toggle_code_match(qubit, low, high, value):
        """Condition qubit on a two-bit code equalling value."""
        if value == 0:
            qc.x(low)
            qc.x(high)
        elif value == 1:
            qc.x(high)
        elif value == 2:
            qc.x(low)
        # value == 3 needs no inverted controls

    def untoggle_code_match(qubit, low, high, value):
        if value == 0:
            qc.x(high)
            qc.x(low)
        elif value == 1:
            qc.x(high)
        elif value == 2:
            qc.x(low)

    def edge_equal(target, u, v):
        """Toggle target iff decoded colors at u and v are equal."""
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Decoded-color equality consists of:
        # color 0: any pairing of codes 00 and 11;
        # color 1: 01 with 01; color 2: 10 with 10.
        for cu, cv in ((0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (2, 2)):
            toggle_code_match(target, ul, uh, cu)
            toggle_code_match(target, vl, vh, cv)
            qc.mcx([ul, uh, vl, vh], target)
            untoggle_code_match(target, vl, vh, cv)
            untoggle_code_match(target, ul, uh, cu)

    def increment_if(control):
        # Descending order ensures all carry controls see their pre-increment values.
        qc.mcx([control, count[0], count[1]], count[2])
        qc.ccx(control, count[0], count[1])
        qc.cx(control, count[0])

    def decrement_if(control):
        # Exact inverse of increment_if.
        qc.cx(control, count[0])
        qc.ccx(control, count[0], count[1])
        qc.mcx([control, count[0], count[1]], count[2])

    # Count monochromatic edges modulo 8.  There are at most seven, so zero
    # uniquely means that every edge is properly colored.
    for u, v in edges:
        edge_equal(flag, u, v)
        increment_if(flag)
        edge_equal(flag, u, v)

    # Apply the marked phase exactly when the counter is zero.
    qc.x(count[0])
    qc.x(count[1])
    qc.x(count[2])
    qc.mcp(math.pi, [count[0], count[1]], count[2])
    qc.x(count[2])
    qc.x(count[1])
    qc.x(count[0])

    # Uncompute the counter and all temporary edge flags.
    for u, v in reversed(edges):
        edge_equal(flag, u, v)
        decrement_if(flag)
        edge_equal(flag, u, v)
```
