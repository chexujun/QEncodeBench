```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_flag = ancilla_qubits[0]
    count = ancilla_qubits[1:4]  # Little-endian, stores number of bad edges mod 8.
    dirty = count[:2]

    edges = [(0, 1), (0, 2), (1, 4), (1, 5), (2, 3), (3, 4), (4, 5)]

    # The six code-pair patterns that decode to equal colors:
    # 00/00, 00/11, 11/00, 11/11 (all color 0), plus 01/01 and 10/10.
    equal_patterns = [
        (0, 0, 0, 0),
        (0, 0, 1, 1),
        (1, 1, 0, 0),
        (1, 1, 1, 1),
        (1, 0, 1, 0),
        (0, 1, 0, 1),
    ]

    def compute_equal(u, v):
        qubits = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]
        for pattern in equal_patterns:
            for q, bit in zip(qubits, pattern):
                if bit == 0:
                    qc.x(q)
            qc.mcx(qubits, edge_flag, ancilla_qubits=dirty, mode="v-chain-dirty")
            for q, bit in reversed(list(zip(qubits, pattern))):
                if bit == 0:
                    qc.x(q)

    def increment_if_flagged():
        qc.mcx([edge_flag, count[0], count[1]], count[2])
        qc.ccx(edge_flag, count[0], count[1])
        qc.cx(edge_flag, count[0])

    def decrement_if_flagged():
        qc.cx(edge_flag, count[0])
        qc.ccx(edge_flag, count[0], count[1])
        qc.mcx([edge_flag, count[0], count[1]], count[2])

    # Count monochromatic edges.
    for u, v in edges:
        compute_equal(u, v)
        increment_if_flagged()
        compute_equal(u, v)

    # Phase-mark exactly the count == 0 subspace.
    for q in count:
        qc.x(q)
    qc.x(edge_flag)
    qc.h(edge_flag)
    qc.mcx(count, edge_flag)
    qc.h(edge_flag)
    qc.x(edge_flag)
    for q in reversed(count):
        qc.x(q)

    # Uncompute the edge-violation count.
    for u, v in reversed(edges):
        compute_equal(u, v)
        decrement_if_flagged()
        compute_equal(u, v)
```
