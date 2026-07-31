```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 2), (0, 3), (0, 4),
             (1, 2), (2, 3), (2, 4))
    flags = ancilla_qubits[:7]

    def toggle_different(u: int, v: int, target: int) -> None:
        a = problem_qubits[2 * u]
        A = problem_qubits[2 * u + 1]
        b = problem_qubits[2 * v]
        B = problem_qubits[2 * v + 1]

        # Algebraic normal form of decoded_color(u) != decoded_color(v):
        # a ⊕ A ⊕ b ⊕ B ⊕ Ab ⊕ aB
        #   ⊕ aAb ⊕ aAB ⊕ abB ⊕ AbB
        qc.cx(a, target)
        qc.cx(A, target)
        qc.cx(b, target)
        qc.cx(B, target)
        qc.ccx(A, b, target)
        qc.ccx(a, B, target)
        qc.mcx([a, A, b], target)
        qc.mcx([a, A, B], target)
        qc.mcx([a, b, B], target)
        qc.mcx([A, b, B], target)

    for (u, v), flag in zip(edges, flags):
        toggle_different(u, v, flag)

    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_different(u, v, flag)
```
