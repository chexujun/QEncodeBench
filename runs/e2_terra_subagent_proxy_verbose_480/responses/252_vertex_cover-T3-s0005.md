```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_flags = ancilla_qubits[:10]
    sum_bits = ancilla_qubits[10:13]  # little-endian population count
    s0, s1, s2 = sum_bits

    edges = [
        (0, 2), (0, 3), (0, 4), (0, 5), (1, 3),
        (1, 5), (2, 3), (2, 5), (3, 4), (4, 5),
    ]

    # Compute an uncovered-edge flag for each edge.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly compute the six-bit population count modulo 8.
    for q in problem_qubits:
        qc.mcx([q, s0, s1], s2)
        qc.ccx(q, s0, s1)
        qc.cx(q, s0)

    # Mark iff all edge flags are zero and the count is at most 3 (s2 == 0).
    condition_qubits = edge_flags + [s2]
    for q in condition_qubits:
        qc.x(q)
    qc.mcp(math.pi, condition_qubits[:-1], condition_qubits[-1])
    for q in reversed(condition_qubits):
        qc.x(q)

    # Uncompute population count.
    for q in reversed(problem_qubits):
        qc.cx(q, s0)
        qc.ccx(q, s0, s1)
        qc.mcx([q, s0, s1], s2)

    # Uncompute uncovered-edge flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
