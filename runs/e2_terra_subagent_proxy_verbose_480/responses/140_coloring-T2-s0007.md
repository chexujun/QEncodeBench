```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_flags = ancilla_qubits[:6]
    marker = ancilla_qubits[6]
    edges = [(0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]

    def toggle_monochromatic(a0, a1, b0, b1, target):
        # Both codes decode to color 0 exactly when their two bits are equal.
        qc.cx(a1, a0)
        qc.cx(b1, b0)
        qc.x(a0)
        qc.x(b0)
        qc.ccx(a0, b0, target)
        qc.x(b0)
        qc.x(a0)
        qc.cx(b1, b0)
        qc.cx(a1, a0)

        # Both decode to color 1: 01, 01.
        qc.x(a1)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b1)
        qc.x(a1)

        # Both decode to color 2: 10, 10.
        qc.x(a0)
        qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0)
        qc.x(a0)

    for flag, (u, v) in zip(edge_flags, edges):
        toggle_monochromatic(
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
            flag,
        )
        qc.x(flag)  # flag = 1 iff this edge's endpoint colors differ

    qc.mcx(edge_flags, marker)
    qc.z(marker)
    qc.mcx(edge_flags, marker)

    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(flag)
        toggle_monochromatic(
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
            flag,
        )
```
