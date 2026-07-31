```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Ten ancillas hold the edge-coverage predicates; three hold popcount.
    edge_flags = ancilla_qubits[:10]
    count = ancilla_qubits[10:13]  # little-endian three-bit counter
    c0, c1, c2 = count

    edges = [
        (0, 1), (0, 2), (0, 3), (0, 5), (1, 2),
        (1, 3), (1, 4), (1, 5), (3, 5), (4, 5),
    ]

    def compute_covered_edge(u, v, target):
        # target = x_u OR x_v, starting with target == 0.
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], target)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    def increment_if(control):
        # Reversibly add control to the three-bit little-endian counter.
        qc.mcx([control, c0, c1], c2)
        qc.ccx(control, c0, c1)
        qc.cx(control, c0)

    def decrement_if(control):
        # Inverse of increment_if.
        qc.cx(control, c0)
        qc.ccx(control, c0, c1)
        qc.mcx([control, c0, c1], c2)

    # Compute all edge-coverage bits.
    for (u, v), flag in zip(edges, edge_flags):
        compute_covered_edge(u, v, flag)

    # Compute the Hamming weight of the selected vertices.
    for vertex in problem_qubits:
        increment_if(vertex)

    # Phase every vertex cover, then cancel the phase for weights 5 and 6.
    qc.mcp(3.141592653589793, edge_flags)

    # weight == 5: counter = 101
    qc.x(c1)
    qc.mcp(3.141592653589793, edge_flags + count)
    qc.x(c1)

    # weight == 6: counter = 110
    qc.x(c0)
    qc.mcp(3.141592653589793, edge_flags + count)
    qc.x(c0)

    # Uncompute the Hamming weight.
    for vertex in reversed(problem_qubits):
        decrement_if(vertex)

    # Uncompute edge-coverage bits.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_covered_edge(u, v, flag)
```
