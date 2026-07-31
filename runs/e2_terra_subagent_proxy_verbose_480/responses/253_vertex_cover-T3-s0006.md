```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Eight ancillas hold the edge-coverage clauses; the final three hold
    # the population count of the selected vertices modulo 8.
    clause = ancilla_qubits[:8]
    count = ancilla_qubits[8:11]

    edges = (
        (0, 1), (0, 2), (0, 4), (1, 2),
        (1, 4), (2, 3), (2, 5), (4, 5),
    )

    # Compute each clause: clause[e] = x[u] OR x[v].
    for a, (u, v) in zip(clause, edges):
        qc.cx(problem_qubits[u], a)
        qc.cx(problem_qubits[v], a)
        qc.ccx(problem_qubits[u], problem_qubits[v], a)

    # Reversibly add each selected vertex into a three-bit counter.
    # Gates are ordered from high carry to low bit for a controlled increment.
    c0, c1, c2 = count
    for q in problem_qubits:
        qc.mcx([q, c0, c1], c2)
        qc.ccx(q, c0, c1)
        qc.cx(q, c0)

    # A vertex cover satisfying all clauses has size at least three
    # (the graph contains a matching of size three), so size <= 3 means
    # the counter must equal 3, i.e. binary 011.
    qc.x(c2)
    qc.mcp(math.pi, clause[1:] + count, clause[0])
    qc.x(c2)

    # Uncompute the population count.
    for q in reversed(problem_qubits):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.mcx([q, c0, c1], c2)

    # Uncompute edge-coverage clauses.
    for a, (u, v) in reversed(list(zip(clause, edges))):
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.cx(problem_qubits[v], a)
        qc.cx(problem_qubits[u], a)
```
