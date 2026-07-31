```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edge_flags = ancilla_qubits[:8]
    count_bad = ancilla_qubits[8]
    phase_target = ancilla_qubits[9]

    edges = [
        (0, 1), (0, 2), (0, 4), (1, 3),
        (1, 4), (2, 4), (3, 4), (3, 5),
    ]

    # Compute flags for uncovered edges.
    # Each flag is 1 exactly when both endpoints are absent from the cover.
    for (u, w), flag in zip(edges, edge_flags):
        qc.x(v[u])
        qc.x(v[w])
        qc.ccx(v[u], v[w], flag)
        qc.x(v[w])
        qc.x(v[u])

    # Compute count_bad = 1 iff the Hamming weight of v is at least 5.
    # For weight 5, exactly one 5-subset fires; for weight 6, seven terms
    # fire, so their XOR is also 1.
    for omitted in range(6):
        controls = [v[i] for i in range(6) if i != omitted]
        qc.mcx(controls, count_bad)
    qc.mcx(v, count_bad)

    # Phase kickback: mark iff all edge flags and count_bad are zero.
    qc.x(phase_target)
    qc.h(phase_target)
    qc.mcx(edge_flags + [count_bad], phase_target, ctrl_state="0" * 9)
    qc.h(phase_target)
    qc.x(phase_target)

    # Uncompute the size constraint.
    qc.mcx(v, count_bad)
    for omitted in reversed(range(6)):
        controls = [v[i] for i in range(6) if i != omitted]
        qc.mcx(controls, count_bad)

    # Uncompute uncovered-edge flags.
    for (u, w), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(v[u])
        qc.x(v[w])
        qc.ccx(v[u], v[w], flag)
        qc.x(v[w])
        qc.x(v[u])
```
