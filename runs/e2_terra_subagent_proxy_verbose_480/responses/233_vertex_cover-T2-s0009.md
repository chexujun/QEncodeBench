```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edge_anc = ancilla_qubits[:6]
    too_large = ancilla_qubits[6]

    edges = [(0, 3), (0, 4), (1, 2),
             (1, 3), (2, 3), (3, 4)]

    # Compute each edge-covered predicate: u OR v = u XOR v XOR (u AND v).
    for a, (u, v) in zip(edge_anc, edges):
        qc.cx(x[u], a)
        qc.cx(x[v], a)
        qc.ccx(x[u], x[v], a)

    # For five bits, weight >= 4 is the XOR of all five 4-bit products.
    for omitted in range(5):
        qc.mcx([x[i] for i in range(5) if i != omitted], too_large)

    # Phase-flip iff every edge is covered and the size is not greater than 3.
    qc.x(too_large)
    qc.mcp(pi, edge_anc[:5] + [too_large], edge_anc[5])
    qc.x(too_large)

    # Uncompute the cardinality predicate.
    for omitted in reversed(range(5)):
        qc.mcx([x[i] for i in range(5) if i != omitted], too_large)

    # Uncompute the edge predicates.
    for a, (u, v) in reversed(list(zip(edge_anc, edges))):
        qc.ccx(x[u], x[v], a)
        qc.cx(x[v], a)
        qc.cx(x[u], a)
```
