```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # One flag per edge.  A flag is 1 exactly when that edge is
    # monochromatic under the surjective color decoding.
    edge_flags = ancilla_qubits[:4]

    def toggle_minterm(bits, values, target):
        """XOR target with 1 iff the four listed bits equal values."""
        zero_controls = []
        for qubit, value in zip(bits, values):
            if value == 0:
                qc.x(qubit)
                zero_controls.append(qubit)
        qc.mcx(bits, target)
        for qubit in reversed(zero_controls):
            qc.x(qubit)

    def compute_same_color(v1, v2, target):
        a0, a1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]
        b0, b1 = problem_qubits[2 * v2], problem_qubits[2 * v2 + 1]
        bits = [a0, a1, b0, b1]

        # Decoded color 0: either code 00 or code 11 for each endpoint.
        for av in ((0, 0), (1, 1)):
            for bv in ((0, 0), (1, 1)):
                toggle_minterm(bits, [av[0], av[1], bv[0], bv[1]], target)

        # Decoded colors 1 and 2.
        toggle_minterm(bits, [1, 0, 1, 0], target)  # 01, 01
        toggle_minterm(bits, [0, 1, 0, 1], target)  # 10, 10

    edges = [(0, 1), (1, 2), (1, 3), (2, 3)]

    # Compute edge-violation flags.
    for (u, v), flag in zip(edges, edge_flags):
        compute_same_color(u, v, flag)

    # Apply phase -1 precisely when no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcp(math.pi, edge_flags[:-1], edge_flags[-1])
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute all flags, restoring every ancilla to |0>.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_same_color(u, v, flag)
```
