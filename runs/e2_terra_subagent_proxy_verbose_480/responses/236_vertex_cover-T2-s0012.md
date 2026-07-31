```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edge_flags = ancilla_qubits[:6]
    counter = ancilla_qubits[6:9]

    edges = (
        (0, 2),
        (0, 4),
        (1, 2),
        (1, 3),
        (1, 4),
        (2, 3),
    )

    # Compute each edge-covered predicate: flag = x_u OR x_v.
    for (u, v), flag in zip(edges, edge_flags):
        qc.cx(x[u], flag)
        qc.cx(x[v], flag)
        qc.ccx(x[u], x[v], flag)

    # Compute the Hamming weight of x into a three-bit counter.
    for bit in x:
        qc.mcx([bit, counter[0], counter[1]], counter[2])
        qc.ccx(bit, counter[0], counter[1])
        qc.cx(bit, counter[0])

    # Since the weight is in 0..5, weight <= 3 iff counter[2] == 0.
    # Apply a phase when all edge flags are 1 and counter[2] is 0.
    qc.x(counter[2])
    qc.h(edge_flags[-1])
    qc.mcx(edge_flags[:-1] + [counter[2]], edge_flags[-1])
    qc.h(edge_flags[-1])
    qc.x(counter[2])

    # Uncompute the Hamming-weight counter.
    for bit in reversed(x):
        qc.cx(bit, counter[0])
        qc.ccx(bit, counter[0], counter[1])
        qc.mcx([bit, counter[0], counter[1]], counter[2])

    # Uncompute all edge-covered flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.ccx(x[u], x[v], flag)
        qc.cx(x[v], flag)
        qc.cx(x[u], flag)
```
