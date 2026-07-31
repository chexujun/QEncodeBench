```python
def build_oracle(qc, q, anc):
    edges = ((0, 1), (0, 2), (0, 3), (1, 3), (2, 3))
    equal_pairs = ((0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0))
    def toggle_edge_difference(u, v, target):
        controls = (q[2 * u], q[2 * u + 1], q[2 * v], q[2 * v + 1]); qc.x(target)
        for bits in equal_pairs:
            for wire, bit in zip(controls, bits):
                if bit == 0: qc.x(wire)
            qc.mcx(controls, target)
            for wire, bit in zip(controls, bits):
                if bit == 0: qc.x(wire)
    for i, (u, v) in enumerate(edges): toggle_edge_difference(u, v, anc[i])
    qc.mcx(anc[:5], anc[5]); qc.z(anc[5]); qc.mcx(anc[:5], anc[5])
    for i, (u, v) in reversed(tuple(enumerate(edges))): toggle_edge_difference(u, v, anc[i])
```
