```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Nine flags: 1 iff the corresponding edge is uncovered.
    edge_flags = ancilla_qubits[:9]
    count_bits = ancilla_qubits[9:12]  # Little-endian 3-bit population count.
    c0, c1, c2 = count_bits

    edges = [
        (0, 3), (0, 5), (1, 3), (1, 4), (1, 5),
        (2, 3), (2, 4), (2, 5), (3, 5),
    ]

    # Compute uncovered-edge flags.  Temporarily complementing vertex bits
    # makes a CCX fire exactly when both endpoints are absent from the cover.
    for q in problem_qubits:
        qc.x(q)
    for flag, (u, v) in zip(edge_flags, edges):
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
    for q in problem_qubits:
        qc.x(q)

    # Compute the Hamming weight of the six vertex-selection bits.
    for q in problem_qubits:
        qc.mcx([q, c0, c1], c2)
        qc.ccx(q, c0, c1)
        qc.cx(q, c0)

    # Use positive controls for "all edges covered".
    for flag in edge_flags:
        qc.x(flag)

    # Phase -1 for every vertex cover.
    qc.mcp(math.pi, edge_flags[:8], edge_flags[8])

    # Cancel that phase for weights 5 (101) and 6 (110).
    # Weight 5: c2=1, c1=0, c0=1.
    qc.x(c1)
    qc.mcp(math.pi, edge_flags + [c2], c0)
    qc.x(c1)

    # Weight 6: c2=1, c1=1, c0=0.
    qc.x(c0)
    qc.mcp(math.pi, edge_flags + [c2, c1], c0)
    qc.x(c0)

    for flag in edge_flags:
        qc.x(flag)

    # Uncompute the population count.
    for q in reversed(problem_qubits):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.mcx([q, c0, c1], c2)

    # Uncompute uncovered-edge flags.
    for q in problem_qubits:
        qc.x(q)
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
    for q in problem_qubits:
        qc.x(q)
```
