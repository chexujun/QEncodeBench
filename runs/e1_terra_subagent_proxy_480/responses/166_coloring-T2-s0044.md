```python
def build_oracle(qc, q, anc):
    edges = ((0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (3, 4))
    def toggle_edge_difference(u, v, target):
        a, b = q[2 * u], q[2 * u + 1]; c, d = q[2 * v], q[2 * v + 1]
        qc.cx(a, target); qc.cx(b, target); qc.cx(c, target); qc.cx(d, target)
        qc.ccx(a, d, target); qc.ccx(b, c, target)
        qc.mcx([a, c, d], target); qc.mcx([a, b, c], target); qc.mcx([a, b, d], target); qc.mcx([b, c, d], target)
    for (u, v), target in zip(edges, anc[:6]): toggle_edge_difference(u, v, target)
    qc.x(anc[6]); qc.h(anc[6]); qc.mcx(list(anc[:6]), anc[6]); qc.h(anc[6]); qc.x(anc[6])
    for (u, v), target in reversed(list(zip(edges, anc[:6]))): toggle_edge_difference(u, v, target)
```
