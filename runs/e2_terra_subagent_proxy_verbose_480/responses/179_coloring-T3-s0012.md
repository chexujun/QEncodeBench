```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    def code_bits(vertex):
        return problem_qubits[2 * vertex], problem_qubits[2 * vertex + 1]

    # Toggles target iff the two vertices decode to the same color.
    # Equal decoded colors comprise four (0, 0) encodings plus (1, 1)
    # and (2, 2), all disjoint cases.
    def toggle_equal(target, u, v):
        u0, u1 = code_bits(u)
        v0, v1 = code_bits(v)
        for cu, cv in ((0, 0), (3, 0), (0, 3), (3, 3), (1, 1), (2, 2)):
            bits = (u0, u1, v0, v1)
            values = (cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1)
            for bit, value in zip(bits, values):
                if not value:
                    qc.x(bit)
            qc.mcx(list(bits), target)
            for bit, value in reversed(list(zip(bits, values))):
                if not value:
                    qc.x(bit)

    # Set target to 1 exactly when edge (u, v) is properly colored.
    def compute_good_edge(target, u, v):
        qc.x(target)
        toggle_equal(target, u, v)

    def uncompute_good_edge(target, u, v):
        toggle_equal(target, u, v)
        qc.x(target)

    first_edges = ((0, 2), (0, 4), (1, 2))
    later_edges = ((1, 4), (2, 3), (2, 4))

    # a0 = AND of the first three edge constraints.
    for target, edge in zip((a1, a2, a3), first_edges):
        compute_good_edge(target, *edge)
    qc.mcx([a1, a2, a3], a0)
    for target, edge in reversed(list(zip((a1, a2, a3), first_edges))):
        uncompute_good_edge(target, *edge)

    # a1..a3 hold the next three edge constraints.
    for target, edge in zip((a1, a2, a3), later_edges):
        compute_good_edge(target, *edge)

    # Apply -1 if the first six constraints hold.
    qc.mcp(math.pi, [a0, a1, a2], a3)

    # Cancel that phase when the final edge (3, 4) is monochromatic.
    # Thus the net phase is -1 exactly when all seven constraints hold.
    u0, u1 = code_bits(3)
    v0, v1 = code_bits(4)
    for cu, cv in ((0, 0), (3, 0), (0, 3), (3, 3), (1, 1), (2, 2)):
        bits = (u0, u1, v0, v1)
        values = (cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1)
        target = v1
        controls = [a0, a1, a2, a3, u0, u1, v0]
        for bit, value in zip(bits, values):
            if not value:
                qc.x(bit)
        qc.mcp(math.pi, controls, target)
        for bit, value in reversed(list(zip(bits, values))):
            if not value:
                qc.x(bit)

    for target, edge in reversed(list(zip((a1, a2, a3), later_edges))):
        uncompute_good_edge(target, *edge)

    # Uncompute a0.
    for target, edge in zip((a1, a2, a3), first_edges):
        compute_good_edge(target, *edge)
    qc.mcx([a1, a2, a3], a0)
    for target, edge in reversed(list(zip((a1, a2, a3), first_edges))):
        uncompute_good_edge(target, *edge)
```
