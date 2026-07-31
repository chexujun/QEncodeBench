```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x = problem_qubits
    edge_flags = ancilla_qubits[:5]
    count = ancilla_qubits[5:8]  # little-endian 3-bit population counter
    c0, c1, c2 = count

    edges = [(0, 2), (0, 4), (1, 3), (2, 3), (3, 4)]

    # Compute whether every edge is covered: flag = x_u OR x_v.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.cx(x[u], flag)
        qc.cx(x[v], flag)
        qc.ccx(x[u], x[v], flag)

    # Compute the Hamming weight of x into count.
    for bit in x:
        qc.mcx([bit, c0, c1], c2)
        qc.ccx(bit, c0, c1)
        qc.cx(bit, c0)

    # Since there are only five vertices, weight <= 3 iff c2 == 0.
    qc.x(c2)
    qc.mcp(math.pi, edge_flags[:4] + [c2], edge_flags[4])
    qc.x(c2)

    # Uncompute population count.
    for bit in reversed(x):
        qc.cx(bit, c0)
        qc.ccx(bit, c0, c1)
        qc.mcx([bit, c0, c1], c2)

    # Uncompute edge-coverage flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.ccx(x[u], x[v], flag)
        qc.cx(x[v], flag)
        qc.cx(x[u], flag)
```
