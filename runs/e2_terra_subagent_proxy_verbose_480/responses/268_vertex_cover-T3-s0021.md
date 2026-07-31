```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Nine ancillas flag uncovered edges; three ancillas hold the Hamming weight.
    edge_flags = ancilla_qubits[:9]
    count = ancilla_qubits[9:12]
    c0, c1, c2 = count

    edges = [
        (0, 1), (1, 2), (1, 4), (1, 5), (2, 3),
        (2, 5), (3, 4), (3, 5), (4, 5),
    ]

    # Compute an uncovered-edge flag: flag = 1 iff both endpoints are zero.
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly accumulate the six-bit Hamming weight into a three-bit counter.
    for x in problem_qubits:
        qc.mcx([x, c0, c1], c2)
        qc.ccx(x, c0, c1)
        qc.cx(x, c0)

    # A weight at most three is exactly c2 == 0.  Also require every
    # uncovered-edge flag to be zero.  Convert these conditions to ones.
    for flag in edge_flags:
        qc.x(flag)
    qc.x(c2)

    # Controlled phase -1 when all nine edge conditions and c2 are satisfied.
    qc.mcp(math.pi, edge_flags[1:] + [c2], edge_flags[0])

    qc.x(c2)
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute the population count.
    for x in reversed(problem_qubits):
        qc.cx(x, c0)
        qc.ccx(x, c0, c1)
        qc.mcx([x, c0, c1], c2)

    # Uncompute uncovered-edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
