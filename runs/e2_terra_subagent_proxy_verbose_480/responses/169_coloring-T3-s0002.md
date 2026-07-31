```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def toggle_equal(u: int, v: int, target: int, reverse: bool = False) -> None:
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        operations = [
            ("x", (target,)),
            ("cx", (u0, target)),
            ("cx", (u1, target)),
            ("cx", (v0, target)),
            ("ccx", (u1, v0, target)),
            ("mcx", ((u0, u1, v0), target)),
            ("cx", (v1, target)),
            ("ccx", (u0, v1, target)),
            ("mcx", ((u0, u1, v1), target)),
            ("mcx", ((u0, v0, v1), target)),
            ("mcx", ((u1, v0, v1), target)),
        ]
        if reverse:
            operations.reverse()

        for gate, args in operations:
            if gate == "x":
                qc.x(args[0])
            elif gate == "cx":
                qc.cx(args[0], args[1])
            elif gate == "ccx":
                qc.ccx(args[0], args[1], args[2])
            else:
                qc.mcx(list(args[0]), args[1])

    def compute_different(u: int, v: int, target: int) -> None:
        toggle_equal(u, v, target)
        qc.x(target)

    def uncompute_different(u: int, v: int, target: int) -> None:
        qc.x(target)
        toggle_equal(u, v, target, reverse=True)

    a0, a1, a2, a3 = ancilla_qubits[:4]

    # First three constraints, reduced to one clean conjunction in a3.
    compute_different(0, 2, a0)
    compute_different(0, 5, a1)
    compute_different(1, 2, a2)
    qc.mcx([a0, a1, a2], a3)
    uncompute_different(1, 2, a2)
    uncompute_different(0, 5, a1)
    uncompute_different(0, 2, a0)

    # Next two constraints, reduced to a2.
    compute_different(1, 3, a0)
    compute_different(2, 3, a1)
    qc.ccx(a0, a1, a2)
    uncompute_different(2, 3, a1)
    uncompute_different(1, 3, a0)

    # The final two constraints occupy a0 and a1.
    compute_different(3, 4, a0)
    compute_different(3, 5, a1)

    # Controlled-Z on the four conjunction/constraint bits.
    qc.h(a1)
    qc.mcx([a3, a2, a0], a1)
    qc.h(a1)

    uncompute_different(3, 5, a1)
    uncompute_different(3, 4, a0)

    qc.ccx(a0, a1, a2)
    # a0 and a1 are already zero here; restore the second conjunction.
    # Recompute/uncompute its original leaves in reverse to clean a2.
    compute_different(1, 3, a0)
    compute_different(2, 3, a1)
    qc.ccx(a0, a1, a2)
    uncompute_different(2, 3, a1)
    uncompute_different(1, 3, a0)

    # Restore the first conjunction.
    compute_different(0, 2, a0)
    compute_different(0, 5, a1)
    compute_different(1, 2, a2)
    qc.mcx([a0, a1, a2], a3)
    uncompute_different(1, 2, a2)
    uncompute_different(0, 5, a1)
    uncompute_different(0, 2, a0)
```
