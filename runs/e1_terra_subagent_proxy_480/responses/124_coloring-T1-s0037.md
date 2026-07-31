```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def edge_equal(v: int, w: int, target: int) -> None:
        p = problem_qubits[2 * v]
        q = problem_qubits[2 * v + 1]
        r = problem_qubits[2 * w]
        s = problem_qubits[2 * w + 1]

        qc.x(target)
        for bit in (p, q, r, s):
            qc.cx(bit, target)
        qc.ccx(p, s, target)
        qc.ccx(q, r, target)
        qc.mcx([p, q, r], target)
        qc.mcx([p, r, s], target)
        qc.mcx([p, q, s], target)
        qc.mcx([q, r, s], target)

    edges = [(0, 1), (0, 2), (1, 2), (1, 3)]
    flags = ancilla_qubits[:4]

    for (v, w), flag in zip(edges, flags):
        edge_equal(v, w, flag)

    for flag in flags:
        qc.x(flag)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for flag in flags:
        qc.x(flag)

    for (v, w), flag in reversed(list(zip(edges, flags))):
        edge_equal(v, w, flag)
```
