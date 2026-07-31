```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 2), (0, 3), (1, 2),
             (1, 3), (2, 4), (3, 4))
    flags = ancilla_qubits[:6]

    def toggle_different(u: int, v: int, target: int) -> None:
        u0 = problem_qubits[2 * u]
        u1 = problem_qubits[2 * u + 1]
        v0 = problem_qubits[2 * v]
        v1 = problem_qubits[2 * v + 1]

        # ANF of decoded_color(u) != decoded_color(v):
        # u0 ^ u1 ^ v0 ^ v1 ^ u1*v0 ^ u0*v1
        # ^ u0*u1*v0 ^ u0*u1*v1 ^ u0*v0*v1 ^ u1*v0*v1
        qc.cx(u0, target)
        qc.cx(u1, target)
        qc.cx(v0, target)
        qc.ccx(u1, v0, target)
        qc.mcx([u0, u1, v0], target)
        qc.cx(v1, target)
        qc.ccx(u0, v1, target)
        qc.mcx([u0, u1, v1], target)
        qc.mcx([u0, v0, v1], target)
        qc.mcx([u1, v0, v1], target)

    def untoggle_different(u: int, v: int, target: int) -> None:
        u0 = problem_qubits[2 * u]
        u1 = problem_qubits[2 * u + 1]
        v0 = problem_qubits[2 * v]
        v1 = problem_qubits[2 * v + 1]

        qc.mcx([u1, v0, v1], target)
        qc.mcx([u0, v0, v1], target)
        qc.mcx([u0, u1, v1], target)
        qc.ccx(u0, v1, target)
        qc.cx(v1, target)
        qc.mcx([u0, u1, v0], target)
        qc.ccx(u1, v0, target)
        qc.cx(v0, target)
        qc.cx(u1, target)
        qc.cx(u0, target)

    for (u, v), flag in zip(edges, flags):
        toggle_different(u, v, flag)

    qc.mcp(math.pi, flags[:-1], flags[-1])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        untoggle_different(u, v, flag)
```
