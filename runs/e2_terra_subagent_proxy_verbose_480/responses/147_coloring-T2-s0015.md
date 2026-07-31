```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 3), (0, 4),
             (1, 2), (1, 4), (2, 4))
    flags = ancilla_qubits[:6]
    phase_ancilla = ancilla_qubits[6]

    def toggle_equality(edge: tuple[int, int], flag: int,
                        inverse: bool = False) -> None:
        u, v = edge
        x0 = problem_qubits[2 * u]
        x1 = problem_qubits[2 * u + 1]
        y0 = problem_qubits[2 * v]
        y1 = problem_qubits[2 * v + 1]

        gates = (
            ("x", (flag,)),
            ("cx", (x0, flag)),
            ("cx", (x1, flag)),
            ("cx", (y0, flag)),
            ("cx", (y1, flag)),
            ("ccx", (x1, y0, flag)),
            ("mcx", ([x0, x1, y0], flag)),
            ("ccx", (x0, y1, flag)),
            ("mcx", ([x0, x1, y1], flag)),
            ("mcx", ([x0, y0, y1], flag)),
            ("mcx", ([x1, y0, y1], flag)),
        )

        sequence = reversed(gates) if inverse else gates
        for name, args in sequence:
            getattr(qc, name)(*args)

    for edge, flag in zip(edges, flags):
        toggle_equality(edge, flag)

    for flag in flags:
        qc.x(flag)

    qc.x(phase_ancilla)
    qc.h(phase_ancilla)
    qc.mcx(flags, phase_ancilla)
    qc.h(phase_ancilla)
    qc.x(phase_ancilla)

    for flag in flags:
        qc.x(flag)

    for edge, flag in reversed(tuple(zip(edges, flags))):
        toggle_equality(edge, flag, inverse=True)
```
