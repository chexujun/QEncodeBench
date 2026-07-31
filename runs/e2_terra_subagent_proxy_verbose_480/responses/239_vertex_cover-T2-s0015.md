```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 2), (1, 3), (1, 4), (2, 3), (3, 4))
    edge_flags = ancilla_qubits[:5]
    cover_flag = ancilla_qubits[5]

    # Compute one OR flag for each edge.
    for (u, v), flag in zip(edges, edge_flags):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, flag)
        qc.x(qv)
        qc.x(qu)
        qc.x(flag)

    # cover_flag = AND of all edge-covered flags.
    qc.mcx(edge_flags, cover_flag)

    # Initially mark every vertex cover.
    qc.z(cover_flag)

    # Cancel the phase for covers of size 4 or 5.
    # For Hamming weight w, the product over all four-vertex subsets
    # contributes (-1)^C(w,4), which is -1 exactly for w = 4 or 5.
    for omitted in range(5):
        subset = [problem_qubits[i] for i in range(5) if i != omitted]
        target = subset[-1]
        controls = [cover_flag] + subset[:-1]
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)

    # Uncompute the cover flag and all edge flags.
    qc.mcx(edge_flags, cover_flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        qc.x(flag)
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, flag)
        qc.x(qv)
        qc.x(qu)
```
