```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    lows = [problem_qubits[2 * v] for v in range(5)]
    highs = [problem_qubits[2 * v + 1] for v in range(5)]
    flags = ancilla_qubits[:4]
    edges = ((0, 2), (0, 4), (1, 3), (2, 4))

    # Convert each high bit into low XOR high.
    for low, high in zip(lows, highs):
        qc.cx(low, high)

    def compute_equal(u, v, target):
        hu, hv = highs[u], highs[v]
        lu, lv = lows[u], lows[v]

        # Both transformed high bits are 0: both colors are 0.
        qc.x(hu)
        qc.x(hv)
        qc.ccx(hu, hv, target)
        qc.x(hv)
        qc.x(hu)

        # Both transformed high bits are 1, and low bits are equal.
        qc.ccx(hu, hv, target)
        qc.cx(lu, lv)
        qc.mcx([hu, hv, lv], target)
        qc.cx(lu, lv)

    for (u, v), flag in zip(edges, flags):
        compute_equal(u, v, flag)

    # Mark states where none of the four edges is monochromatic.
    qc.mcp(math.pi, flags[:-1], flags[-1])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_equal(u, v, flag)

    for low, high in reversed(list(zip(lows, highs))):
        qc.cx(low, high)
```
