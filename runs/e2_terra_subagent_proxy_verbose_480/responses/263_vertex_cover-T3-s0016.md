```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x = problem_qubits
    edge_flags = ancilla_qubits[:8]
    count = ancilla_qubits[8:11]  # little-endian 3-bit Hamming-weight counter

    edges = [
        (0, 2), (0, 3), (1, 3), (1, 5),
        (2, 3), (3, 4), (3, 5), (4, 5),
    ]

    # Compute one flag per edge: flag = x[u] OR x[v].
    for flag, (u, v) in zip(edge_flags, edges):
        qc.cx(x[u], flag)
        qc.cx(x[v], flag)
        qc.ccx(x[u], x[v], flag)

    # Compute the Hamming weight of x into count.
    for bit in x:
        qc.mcx([bit, count[0], count[1]], count[2])
        qc.ccx(bit, count[0], count[1])
        qc.cx(bit, count[0])

    # For weights 0..6, weight <= 3 exactly when count[2] == 0.
    qc.x(count[2])
    qc.mcp(math.pi, edge_flags, count[2])
    qc.x(count[2])

    # Uncompute the Hamming weight.
    for bit in reversed(x):
        qc.cx(bit, count[0])
        qc.ccx(bit, count[0], count[1])
        qc.mcx([bit, count[0], count[1]], count[2])

    # Uncompute edge flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.ccx(x[u], x[v], flag)
        qc.cx(x[v], flag)
        qc.cx(x[u], flag)
```
