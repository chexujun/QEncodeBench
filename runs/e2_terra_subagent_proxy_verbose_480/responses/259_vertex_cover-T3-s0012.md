```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x = problem_qubits
    clause = ancilla_qubits[:6]
    valid = ancilla_qubits[6]
    count0, count1, count2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]

    edges = [(0, 1), (1, 4), (1, 5), (2, 3), (2, 5), (3, 5)]

    def compute_clause(u, v, target):
        # target = u OR v, with target initially |0>
        qc.x(u)
        qc.x(v)
        qc.x(target)
        qc.ccx(u, v, target)
        qc.x(v)
        qc.x(u)

    def uncompute_clause(u, v, target):
        qc.x(u)
        qc.x(v)
        qc.ccx(u, v, target)
        qc.x(target)
        qc.x(v)
        qc.x(u)

    def controlled_increment(control):
        # Add control to the three-bit little-endian counter.
        qc.ccx(control, count0, count1, count2)
        qc.ccx(control, count0, count1)
        qc.cx(control, count0)

    def controlled_decrement(control):
        qc.cx(control, count0)
        qc.ccx(control, count0, count1)
        qc.ccx(control, count0, count1, count2)

    # Compute whether every edge is covered.
    for (u, v), target in zip(edges, clause):
        compute_clause(x[u], x[v], target)
    qc.mcx(clause, valid)
    for (u, v), target in reversed(list(zip(edges, clause))):
        uncompute_clause(x[u], x[v], target)

    # Compute the Hamming weight of the selected vertices.
    for bit in x:
        controlled_increment(bit)

    # Mark valid covers whose size is at most 3 (count's top bit is zero).
    qc.x(count2)
    qc.cz(valid, count2)
    qc.x(count2)

    # Uncompute the Hamming-weight counter.
    for bit in reversed(x):
        controlled_decrement(bit)

    # Uncompute the cover-validity flag.
    for (u, v), target in zip(edges, clause):
        compute_clause(x[u], x[v], target)
    qc.mcx(clause, valid)
    for (u, v), target in reversed(list(zip(edges, clause))):
        uncompute_clause(x[u], x[v], target)
```
