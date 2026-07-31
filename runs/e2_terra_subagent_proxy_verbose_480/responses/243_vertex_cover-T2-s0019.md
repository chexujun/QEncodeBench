```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    v = problem_qubits
    edge_flags = ancilla_qubits[:6]
    cover_flag = ancilla_qubits[6]
    too_large_flag = ancilla_qubits[7]

    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (2, 4)]

    # Compute whether each edge is covered: flag = v[u] OR v[w].
    for flag, (u, w) in zip(edge_flags, edges):
        qc.x(flag)
        qc.x(v[u])
        qc.x(v[w])
        qc.ccx(v[u], v[w], flag)
        qc.x(v[w])
        qc.x(v[u])

    # cover_flag = AND(all edge-covered flags).
    qc.mcx(edge_flags, cover_flag)

    # too_large_flag = 1 exactly when the Hamming weight of v is at least 4.
    # XOR of all 4-vertex subsets has this value for five input bits.
    for omitted in range(5):
        controls = [v[i] for i in range(5) if i != omitted]
        qc.mcx(controls, too_large_flag)

    # Apply phase iff this is a cover and its size is at most 3.
    qc.x(too_large_flag)
    qc.cz(cover_flag, too_large_flag)
    qc.x(too_large_flag)

    # Uncompute size test.
    for omitted in reversed(range(5)):
        controls = [v[i] for i in range(5) if i != omitted]
        qc.mcx(controls, too_large_flag)

    # Uncompute cover flag.
    qc.mcx(edge_flags, cover_flag)

    # Uncompute edge-covered flags.
    for flag, (u, w) in reversed(list(zip(edge_flags, edges))):
        qc.x(v[u])
        qc.x(v[w])
        qc.ccx(v[u], v[w], flag)
        qc.x(v[w])
        qc.x(v[u])
```
