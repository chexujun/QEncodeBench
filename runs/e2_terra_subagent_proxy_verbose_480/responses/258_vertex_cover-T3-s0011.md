```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # One ancilla per edge stores whether that edge is uncovered.
    edges = [
        (0, 3), (0, 4), (1, 2), (1, 3), (1, 4),
        (1, 5), (2, 3), (2, 4), (3, 5), (4, 5),
    ]
    uncovered = ancilla_qubits[:10]
    count = ancilla_qubits[10:13]  # Little-endian 3-bit Hamming-weight counter

    # Compute edge-uncovered flags: e = (not x_u) and (not x_v).
    for (u, v), flag in zip(edges, uncovered):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly accumulate the six input bits into count modulo 8.
    for q in problem_qubits:
        qc.mcx([q, count[0], count[1]], count[2])
        qc.ccx(q, count[0], count[1])
        qc.cx(q, count[0])

    # A weight at most three is exactly count[2] == 0.
    # Also require every uncovered-edge flag to be zero.
    for flag in uncovered:
        qc.x(flag)
    qc.x(count[2])
    qc.mcp(math.pi, uncovered, count[2])
    qc.x(count[2])
    for flag in reversed(uncovered):
        qc.x(flag)

    # Uncompute the Hamming-weight counter.
    for q in reversed(problem_qubits):
        qc.cx(q, count[0])
        qc.ccx(q, count[0], count[1])
        qc.mcx([q, count[0], count[1]], count[2])

    # Uncompute edge-uncovered flags.
    for (u, v), flag in reversed(list(zip(edges, uncovered))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
