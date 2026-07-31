```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Algebraic-normal-form terms for equality of two decoded colors.
    # Variables are (a0, a1, b0, b1), where 00 and 11 both decode to color 0.
    equality_terms = (
        (),
        (0,),
        (1,),
        (2,),
        (1, 2),
        (0, 1, 2),
        (3,),
        (0, 3),
        (0, 1, 3),
        (0, 2, 3),
        (1, 2, 3),
    )

    def compute_equal(target: int, vertex_a: int, vertex_b: int) -> None:
        bits = (
            problem_qubits[2 * vertex_a],
            problem_qubits[2 * vertex_a + 1],
            problem_qubits[2 * vertex_b],
            problem_qubits[2 * vertex_b + 1],
        )
        for term in equality_terms:
            if len(term) == 0:
                qc.x(target)
            elif len(term) == 1:
                qc.cx(bits[term[0]], target)
            else:
                qc.mcx([bits[i] for i in term], target)

    edges = ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3))
    edge_is_different = ancilla_qubits[:5]
    phase_workspace = ancilla_qubits[5]

    # Compute one "colors differ" flag per edge.
    for flag, (u, v) in zip(edge_is_different, edges):
        compute_equal(flag, u, v)
        qc.x(flag)

    # Apply phase iff all five edge constraints hold.
    qc.mcx(edge_is_different, phase_workspace)
    qc.z(phase_workspace)
    qc.mcx(edge_is_different, phase_workspace)

    # Uncompute all flags.
    for flag, (u, v) in reversed(list(zip(edge_is_different, edges))):
        qc.x(flag)
        compute_equal(flag, u, v)
```
