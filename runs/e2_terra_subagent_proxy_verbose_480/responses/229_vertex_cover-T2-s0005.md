```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edge_flags = ancilla_qubits[:6]
    bad_size = ancilla_qubits[6]
    cover_flag = ancilla_qubits[7]

    edges = (
        (0, 1),
        (0, 3),
        (0, 4),
        (1, 3),
        (1, 4),
        (2, 3),
    )

    # Compute one flag for each covered edge:
    # u OR v = u XOR v XOR (u AND v).
    for flag, (u, v) in zip(edge_flags, edges):
        qc.cx(x[u], flag)
        qc.cx(x[v], flag)
        qc.ccx(x[u], x[v], flag)

    # bad_size = 1 exactly when the Hamming weight is 4 or 5.
    # The XOR of all five four-variable products has this property.
    for omitted in range(5):
        controls = [x[i] for i in range(5) if i != omitted]
        qc.mcx(controls, bad_size)

    # Compute whether every edge is covered.
    qc.mcx(edge_flags, cover_flag)

    # Apply -1 exactly when cover_flag = 1 and bad_size = 0.
    qc.x(bad_size)
    qc.cz(bad_size, cover_flag)
    qc.x(bad_size)

    # Uncompute all predicate workspace.
    qc.mcx(edge_flags, cover_flag)

    for omitted in reversed(range(5)):
        controls = [x[i] for i in range(5) if i != omitted]
        qc.mcx(controls, bad_size)

    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.ccx(x[u], x[v], flag)
        qc.cx(x[v], flag)
        qc.cx(x[u], flag)
```
