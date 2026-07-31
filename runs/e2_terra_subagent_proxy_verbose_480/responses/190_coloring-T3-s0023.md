```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Change each vertex representation from (b0, b1) to (b0 XOR b1, b1).
    # In this representation:
    #   color 0: low == 0 (either original 00 or 11)
    #   color 1: low, high == 1, 0
    #   color 2: low, high == 1, 1
    for v in range(5):
        qc.cx(problem_qubits[2 * v + 1], problem_qubits[2 * v])

    def equality_flag(u: int, v: int, target: int) -> None:
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Both vertices have color 0.
        qc.x(ul)
        qc.x(vl)
        qc.ccx(ul, vl, target)
        qc.x(vl)
        qc.x(ul)

        # Both vertices have color 1.
        qc.x(uh)
        qc.x(vh)
        qc.mcx([ul, uh, vl, vh], target)
        qc.x(vh)
        qc.x(uh)

        # Both vertices have color 2.
        qc.mcx([ul, uh, vl, vh], target)

    def equality_flag_inverse(u: int, v: int, target: int) -> None:
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.mcx([ul, uh, vl, vh], target)

        qc.x(uh)
        qc.x(vh)
        qc.mcx([ul, uh, vl, vh], target)
        qc.x(vh)
        qc.x(uh)

        qc.x(ul)
        qc.x(vl)
        qc.ccx(ul, vl, target)
        qc.x(vl)
        qc.x(ul)

    def difference_flag(u: int, v: int, target: int) -> None:
        qc.x(target)
        equality_flag(u, v, target)

    def difference_flag_inverse(u: int, v: int, target: int) -> None:
        equality_flag_inverse(u, v, target)
        qc.x(target)

    a0, a1, a2, a3, a4 = ancilla_qubits

    # The graph is properly colored exactly when:
    # c3 = c0, c4 = c2, and c0, c1, c2 are pairwise different.
    equality_flag(0, 3, a0)
    equality_flag(2, 4, a1)
    difference_flag(0, 1, a2)
    difference_flag(0, 2, a3)
    difference_flag(1, 2, a4)

    # Apply -1 iff every constraint flag is one.
    qc.h(a4)
    qc.mcx([a0, a1, a2, a3], a4)
    qc.h(a4)

    difference_flag_inverse(1, 2, a4)
    difference_flag_inverse(0, 2, a3)
    difference_flag_inverse(0, 1, a2)
    equality_flag_inverse(2, 4, a1)
    equality_flag_inverse(0, 3, a0)

    for v in reversed(range(5)):
        qc.cx(problem_qubits[2 * v + 1], problem_qubits[2 * v])
```
