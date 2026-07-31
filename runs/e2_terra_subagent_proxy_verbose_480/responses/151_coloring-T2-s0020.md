```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = (
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 4), (2, 3), (3, 4),
    )
    edge_flags = ancilla_qubits[:7]
    phase_flag = ancilla_qubits[7]

    # Store p_v = low_v XOR high_v in each high-bit qubit.
    # p_v is zero exactly for the two encodings of color 0.
    for v in range(5):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])

    def toggle_different(u: int, v: int, target: int) -> None:
        low_u = problem_qubits[2 * u]
        parity_u = problem_qubits[2 * u + 1]
        low_v = problem_qubits[2 * v]
        parity_v = problem_qubits[2 * v + 1]

        # different = p_u XOR p_v
        #             XOR (p_u AND p_v AND low_u)
        #             XOR (p_u AND p_v AND low_v)
        qc.cx(parity_u, target)
        qc.cx(parity_v, target)
        qc.mcx([parity_u, parity_v, low_u], target)
        qc.mcx([parity_u, parity_v, low_v], target)

    for (u, v), flag in zip(edges, edge_flags):
        toggle_different(u, v, flag)

    qc.mcx(edge_flags, phase_flag)
    qc.z(phase_flag)
    qc.mcx(edge_flags, phase_flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        toggle_different(u, v, flag)

    for v in reversed(range(5)):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])
```
