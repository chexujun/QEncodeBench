```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 4))
    edge_flags = ancilla_qubits[:6]
    size_flag = ancilla_qubits[6]

    # Compute one flag for each uncovered edge.
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # For five bits, XOR of all degree-four monomials is 1 exactly
    # when the Hamming weight is at least four.
    omitted_vertices = range(5)
    for omitted in omitted_vertices:
        controls = [
            problem_qubits[i] for i in range(5) if i != omitted
        ]
        qc.mcx(controls, size_flag)

    # Mark iff every edge is covered and the size flag is zero.
    predicate_flags = edge_flags + [size_flag]
    for flag in predicate_flags:
        qc.x(flag)
    qc.mcp(math.pi, predicate_flags[:-1], predicate_flags[-1])
    for flag in reversed(predicate_flags):
        qc.x(flag)

    # Uncompute the size flag.
    for omitted in reversed(range(5)):
        controls = [
            problem_qubits[i] for i in range(5) if i != omitted
        ]
        qc.mcx(controls, size_flag)

    # Uncompute all uncovered-edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
