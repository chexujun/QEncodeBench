```python
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Map each encoding so high bits distinguish color 0 from colors 1/2:
    # 00, 11 -> h = 0; 01 -> (l,h) = (1,1); 10 -> (l,h) = (0,1).
    for v in range(5):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])

    edge_flags = ancilla_qubits[:8]
    edges = [
        (0, 1), (0, 3), (0, 4), (1, 2),
        (1, 3), (2, 3), (2, 4), (3, 4),
    ]

    def compute_equal(u, v, target):
        lu, hu = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Both vertices have decoded color 0.
        qc.x(hu)
        qc.x(hv)
        qc.ccx(hu, hv, target)
        qc.x(hv)
        qc.x(hu)

        # Both vertices have decoded color 1.
        qc.mcx([hu, hv, lu, lv], target)

        # Both vertices have decoded color 2.
        qc.x(lu)
        qc.x(lv)
        qc.mcx([hu, hv, lu, lv], target)
        qc.x(lv)
        qc.x(lu)

    # Compute one flag per monochromatic edge.
    for (u, v), flag in zip(edges, edge_flags):
        compute_equal(u, v, flag)

    # Mark exactly when every edge flag is zero.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcp(pi, edge_flags[:-1], edge_flags[-1])
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_equal(u, v, flag)

    # Restore the original vertex encodings.
    for v in reversed(range(5)):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])
```
