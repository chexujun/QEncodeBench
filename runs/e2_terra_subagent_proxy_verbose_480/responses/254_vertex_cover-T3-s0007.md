```python
import math

from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    clauses = ancilla_qubits[:7]
    count_bits = ancilla_qubits[7:10]
    b0, b1, b2 = count_bits

    edges = ((0, 4), (0, 5), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5))

    # Compute each edge-cover clause: c = x_u OR x_v.
    for (u, v), c in zip(edges, clauses):
        qc.cx(problem_qubits[u], c)
        qc.cx(problem_qubits[v], c)
        qc.ccx(problem_qubits[u], problem_qubits[v], c)

    # Reversibly add each selected vertex into a three-bit population count.
    for q in problem_qubits:
        qc.ccx(q, b0, b1, b2)
        qc.ccx(q, b0, b1)
        qc.cx(q, b0)

    # The count is at most six, so weight <= 3 iff b2 is zero.
    # Apply a controlled phase for both possible values of b0.
    qc.x(b2)
    qc.mcp(math.pi, clauses + [b2], b0)
    qc.x(b0)
    qc.mcp(math.pi, clauses + [b2], b0)
    qc.x(b0)
    qc.x(b2)

    # Uncompute the population count.
    for q in reversed(problem_qubits):
        qc.cx(q, b0)
        qc.ccx(q, b0, b1)
        qc.ccx(q, b0, b1, b2)

    # Uncompute edge-cover clauses.
    for (u, v), c in reversed(list(zip(edges, clauses))):
        qc.ccx(problem_qubits[u], problem_qubits[v], c)
        qc.cx(problem_qubits[v], c)
        qc.cx(problem_qubits[u], c)
```
