```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    edge_work = ancilla_qubits[:8]
    cover_flag = ancilla_qubits[8]
    size_flag = ancilla_qubits[9]

    edges = (
        (0, 2), (0, 5), (1, 2), (1, 4),
        (1, 5), (2, 4), (3, 4), (4, 5),
    )

    def compute_edges():
        for target, (u, v) in zip(edge_work, edges):
            # target = p[u] OR p[v]
            qc.cx(p[u], target)
            qc.cx(p[v], target)
            qc.ccx(p[u], p[v], target)

    def uncompute_edges():
        for target, (u, v) in reversed(list(zip(edge_work, edges))):
            qc.ccx(p[u], p[v], target)
            qc.cx(p[v], target)
            qc.cx(p[u], target)

    def compute_size_ok():
        # size_flag = 1 iff the Hamming weight of p is at most 4.
        # "weight >= 5" is the XOR of all 5-way conjunctions and
        # the 6-way conjunction.
        qc.x(size_flag)
        for omitted in range(6):
            qc.mcx([p[i] for i in range(6) if i != omitted], size_flag)
        qc.mcx(p, size_flag)

    def uncompute_size_ok():
        qc.mcx(p, size_flag)
        for omitted in reversed(range(6)):
            qc.mcx([p[i] for i in range(6) if i != omitted], size_flag)
        qc.x(size_flag)

    # Compute whether every edge is covered.
    compute_edges()
    qc.mcx(edge_work, cover_flag)
    uncompute_edges()

    # Compute cardinality condition, phase-mark, then clean up.
    compute_size_ok()
    qc.cz(cover_flag, size_flag)
    uncompute_size_ok()

    # Clean up the vertex-cover flag.
    compute_edges()
    qc.mcx(edge_work, cover_flag)
    uncompute_edges()
```
