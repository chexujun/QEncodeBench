```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edge_flags = ancilla_qubits[:4]
    work = ancilla_qubits[4]

    edges = ((0, 1), (1, 4), (2, 4), (3, 4))

    # Compute each edge-covered predicate:
    # flag = xi OR xj = NOT((NOT xi) AND (NOT xj)).
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(x[u])
        qc.x(x[v])
        qc.ccx(x[u], x[v], flag)
        qc.x(x[v])
        qc.x(x[u])
        qc.x(flag)

    def apply_all_ones_phase(qubits: list[int]) -> None:
        target = qubits[-1]
        controls = qubits[:-1]
        qc.h(target)
        if len(controls) <= 4:
            qc.mcx(controls, target)
        else:
            qc.mcx(controls, target,
                   ancilla_qubits=[work], mode="recursion")
        qc.h(target)

    # First mark every vertex cover.
    apply_all_ones_phase(edge_flags)

    # For five bits, [weight >= 4] is the XOR of the five four-bit
    # conjunctions. Applying these phases cancels covers of size 4 or 5.
    for omitted in range(5):
        four_vertices = [x[i] for i in range(5) if i != omitted]
        apply_all_ones_phase(edge_flags + four_vertices)

    # Uncompute the edge predicates.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(flag)
        qc.x(x[u])
        qc.x(x[v])
        qc.ccx(x[u], x[v], flag)
        qc.x(x[v])
        qc.x(x[u])
```
