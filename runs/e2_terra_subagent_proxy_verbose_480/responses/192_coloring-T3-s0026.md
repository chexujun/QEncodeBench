```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Algebraic-normal-form monomials for:
    # decoded_color(u) != decoded_color(v),
    # with variables [u_low, u_high, v_low, v_high].
    monomials = (1, 2, 4, 6, 7, 8, 9, 11, 13, 14)
    edges = ((0, 1), (0, 4), (0, 5), (1, 3),
             (1, 4), (2, 3), (2, 4), (3, 5))

    def compute_edge_validity(edge_index: int, target: int) -> None:
        u, v = edges[edge_index]
        variables = (
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        )

        for mask in monomials:
            controls = [
                variables[i] for i in range(4) if (mask >> i) & 1
            ]
            if len(controls) == 1:
                qc.cx(controls[0], target)
            elif len(controls) == 2:
                qc.ccx(controls[0], controls[1], target)
            else:
                qc.mcx(controls, target)

    flags = ancilla_qubits[:4]
    first_half_and = ancilla_qubits[4]

    # Compute validity of the first four edges, then retain their AND.
    for i in range(4):
        compute_edge_validity(i, flags[i])
    qc.mcx(flags, first_half_and)
    for i in range(3, -1, -1):
        compute_edge_validity(i, flags[i])

    # Compute validity of the remaining four edges and phase-mark iff all
    # eight validity predicates are true.
    for i in range(4):
        compute_edge_validity(i + 4, flags[i])
    qc.mcp(math.pi, flags, first_half_and)
    for i in range(3, -1, -1):
        compute_edge_validity(i + 4, flags[i])

    # Uncompute the retained AND and restore every ancilla to zero.
    for i in range(4):
        compute_edge_validity(i, flags[i])
    qc.mcx(flags, first_half_and)
    for i in range(3, -1, -1):
        compute_edge_validity(i, flags[i])
```
