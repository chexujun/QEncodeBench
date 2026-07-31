```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 4), (1, 2),
             (1, 4), (2, 3), (3, 4))
    flags = ancilla_qubits[:6]

    def toggle_equal(u: int, v: int, target: int,
                     reverse: bool = False) -> None:
        a0, a1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        b0, b1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        operations = [
            ("x", (target,)),
            ("cx", (a0, target)),
            ("cx", (a1, target)),
            ("cx", (b0, target)),
            ("cx", (b1, target)),
            ("ccx", (a1, b0, target)),
            ("ccx", (a0, b1, target)),
            ("mcx", ([a0, a1, b0], target)),
            ("mcx", ([a0, a1, b1], target)),
            ("mcx", ([a0, b0, b1], target)),
            ("mcx", ([a1, b0, b1], target)),
        ]

        if reverse:
            operations.reverse()

        for gate, args in operations:
            if gate == "x":
                qc.x(*args)
            elif gate == "cx":
                qc.cx(*args)
            elif gate == "ccx":
                qc.ccx(*args)
            else:
                qc.mcx(*args)

    for (u, v), flag in zip(edges, flags):
        toggle_equal(u, v, flag)

    for flag in flags:
        qc.x(flag)

    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])

    for flag in flags:
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_equal(u, v, flag, reverse=True)
```
