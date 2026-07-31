```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edges = ((0, 1), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4))
    edge_flags = ancilla_qubits[:6]
    size_flag = ancilla_qubits[6]

    # Compute one flag per uncovered edge: flag = NOT(x_u) AND NOT(x_v).
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # For five bits, weight >= 4 is the XOR of all five four-bit products.
    # Exactly one product is true at weight 4, and all five are true at weight 5.
    omitted_vertices = range(5)
    for omitted in omitted_vertices:
        controls = [
            problem_qubits[i] for i in range(5) if i != omitted
        ]
        qc.mcx(controls, size_flag)

    # Convert the conditions "no uncovered edges" and "weight < 4"
    # into all-one controls, then apply the phase.
    for flag in edge_flags:
        qc.x(flag)
    qc.x(size_flag)

    phase_qubits = [*edge_flags, size_flag]
    qc.mcp(pi, phase_qubits[:-1], phase_qubits[-1])

    qc.x(size_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute the cardinality flag.
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
