```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    p = problem_qubits
    edge_flags = ancilla_qubits[:6]
    c0, c1, c2 = ancilla_qubits[6:9]

    edges = [(0, 3), (0, 4), (1, 3), (1, 4), (2, 4), (3, 4)]

    # Compute one flag per edge: flag = p[u] OR p[v].
    for (u, v), flag in zip(edges, edge_flags):
        qc.cx(p[u], flag)
        qc.cx(p[v], flag)
        qc.ccx(p[u], p[v], flag)

    # Reversibly count the selected vertices in the three-bit counter.
    for vertex in p:
        qc.ccx(vertex, c0, c1, c2)
        qc.ccx(vertex, c0, c1)
        qc.cx(vertex, c0)

    # The count is at most 3 precisely when c2 is zero.  Apply the phase
    # when all edge flags are set, splitting on p[0] to express a phase
    # independent of the remaining counter bits.
    qc.x(c2)
    controls = edge_flags + [c2]
    qc.x(p[0])
    qc.mcp(math.pi, controls, p[0])
    qc.x(p[0])
    qc.mcp(math.pi, controls, p[0])
    qc.x(c2)

    # Uncompute the population counter.
    for vertex in reversed(p):
        qc.cx(vertex, c0)
        qc.ccx(vertex, c0, c1)
        qc.ccx(vertex, c0, c1, c2)

    # Uncompute edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.ccx(p[u], p[v], flag)
        qc.cx(p[v], flag)
        qc.cx(p[u], flag)
```
