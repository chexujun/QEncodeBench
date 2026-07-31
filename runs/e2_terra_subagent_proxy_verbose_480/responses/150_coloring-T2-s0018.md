```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3))
    flags = ancilla_qubits[:5]

    def toggle_different(u: int, v: int, target: int) -> None:
        a0 = problem_qubits[2 * u]
        a1 = problem_qubits[2 * u + 1]
        b0 = problem_qubits[2 * v]
        b1 = problem_qubits[2 * v + 1]

        qc.cx(a0, target)
        qc.cx(a1, target)
        qc.cx(b0, target)
        qc.ccx(a1, b0, target)
        qc.mcx([a0, a1, b0], target)
        qc.cx(b1, target)
        qc.ccx(a0, b1, target)
        qc.mcx([a0, a1, b1], target)
        qc.mcx([a0, b0, b1], target)
        qc.mcx([a1, b0, b1], target)

    for (u, v), flag in zip(edges, flags):
        toggle_different(u, v, flag)

    qc.mcp(math.pi, flags[:-1], flags[-1])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_different(u, v, flag)
```
