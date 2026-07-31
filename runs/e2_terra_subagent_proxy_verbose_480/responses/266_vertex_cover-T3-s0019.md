```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Nine ancillas hold the edge-covered predicates; the final three
    # reversibly hold the 3-bit Hamming weight of the selected vertices.
    edge_flags = ancilla_qubits[:9]
    count = ancilla_qubits[9:12]  # little-endian: count[0] is the LSB

    edges = [
        (0, 2), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 5),
        (2, 4), (2, 5), (4, 5),
    ]

    # Compute each edge predicate x_u OR x_v.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.cx(problem_qubits[u], flag)
        qc.cx(problem_qubits[v], flag)
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)

    # Reversibly accumulate the number of selected vertices modulo 8.
    # Since there are only six vertices, this is the exact population count.
    for qubit in problem_qubits:
        qc.mcx([qubit, count[0], count[1]], count[2])
        qc.ccx(qubit, count[0], count[1])
        qc.cx(qubit, count[0])

    # Phase every vertex cover, then cancel the phase for weights 5 and 6.
    qc.mcp(math.pi, edge_flags[1:], edge_flags[0])

    # Weight 5 is binary 101.
    qc.x(count[1])
    qc.mcp(math.pi, edge_flags[1:] + count, edge_flags[0])
    qc.x(count[1])

    # Weight 6 is binary 110.
    qc.x(count[0])
    qc.mcp(math.pi, edge_flags[1:] + count, edge_flags[0])
    qc.x(count[0])

    # Uncompute the population count.
    for qubit in reversed(problem_qubits):
        qc.cx(qubit, count[0])
        qc.ccx(qubit, count[0], count[1])
        qc.mcx([qubit, count[0], count[1]], count[2])

    # Uncompute edge predicates.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.cx(problem_qubits[v], flag)
        qc.cx(problem_qubits[u], flag)
```
