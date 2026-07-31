```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = (
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 4), (2, 3), (2, 4),
    )
    edge_flags = ancilla_qubits[:7]

    # Replace each low code bit l_v by u_v = l_v XOR h_v.
    # The decoded color is then:
    #   u=0           -> color 0
    #   u=1, h=0      -> color 1
    #   u=1, h=1      -> color 2
    for v in range(5):
        qc.cx(problem_qubits[2 * v + 1], problem_qubits[2 * v])

    def toggle_edge_difference(v: int, w: int, target: int) -> None:
        uv = problem_qubits[2 * v]
        hv = problem_qubits[2 * v + 1]
        uw = problem_qubits[2 * w]
        hw = problem_qubits[2 * w + 1]

        # diff = uv XOR uw XOR (uv AND uw AND hv)
        #                    XOR (uv AND uw AND hw)
        qc.cx(uv, target)
        qc.cx(uw, target)
        qc.mcx([uv, uw, hv], target)
        qc.mcx([uv, uw, hw], target)

    # Compute one "endpoints have different colors" flag per edge.
    for (v, w), flag in zip(edges, edge_flags):
        toggle_edge_difference(v, w, flag)

    # Apply -1 exactly when all seven edge constraints are satisfied.
    phase_target = edge_flags[-1]
    qc.h(phase_target)
    qc.mcx(edge_flags[:-1], phase_target)
    qc.h(phase_target)

    # Uncompute all edge flags.
    for (v, w), flag in reversed(list(zip(edges, edge_flags))):
        toggle_edge_difference(v, w, flag)

    # Restore the original problem-qubit encoding.
    for v in reversed(range(5)):
        qc.cx(problem_qubits[2 * v + 1], problem_qubits[2 * v])
```
