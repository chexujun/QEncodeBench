```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_flags = ancilla_qubits[:7]
    cover_flag = ancilla_qubits[7]
    count_bits = ancilla_qubits[:3]  # little-endian 3-bit population count

    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 5), (2, 3), (2, 4)]

    # Compute whether each edge is uncovered.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # cover_flag = 1 exactly when no edge is uncovered.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, cover_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute edge flags, freeing them for the population counter.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    c0, c1, c2 = count_bits

    # Compute Hamming weight of the six vertices modulo 8.
    for q in problem_qubits:
        qc.mcx([q, c0, c1], c2)
        qc.ccx(q, c0, c1)
        qc.cx(q, c0)

    # A six-bit weight is at most 3 exactly when its bit 2 is zero.
    qc.x(c2)
    qc.cz(c2, cover_flag)
    qc.x(c2)

    # Uncompute the population counter.
    for q in reversed(problem_qubits):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.mcx([q, c0, c1], c2)

    # Uncompute the vertex-cover flag.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, cover_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)
```
