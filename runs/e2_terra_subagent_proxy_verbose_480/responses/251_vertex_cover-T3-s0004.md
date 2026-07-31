```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_flags = ancilla_qubits[:7]
    count = ancilla_qubits[7:10]
    c0, c1, c2 = count

    edges = [(0, 1), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)]

    # Compute one flag per uncovered edge.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly add each selected vertex to a three-bit population counter.
    for p in problem_qubits:
        qc.mcx([p, c0, c1], c2)
        qc.ccx(p, c0, c1)
        qc.cx(p, c0)

    # A cover has every edge flag equal to zero; size <= 3 means c2 is zero.
    # Convert these zero-controls to one-controls, apply the phase, then restore.
    for flag in edge_flags:
        qc.x(flag)
    qc.x(c2)
    qc.mcp(math.pi, edge_flags, c2)
    qc.x(c2)
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute the population counter.
    for p in reversed(problem_qubits):
        qc.cx(p, c0)
        qc.ccx(p, c0, c1)
        qc.mcx([p, c0, c1], c2)

    # Uncompute edge flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
