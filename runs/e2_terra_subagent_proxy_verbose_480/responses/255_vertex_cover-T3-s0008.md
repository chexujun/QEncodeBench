```python
import itertools
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Seven ancillas hold whether their respective edge is uncovered.
    edge_ancillas = ancilla_qubits[:7]
    threshold_ancilla = ancilla_qubits[7]
    phase_ancilla = ancilla_qubits[8]

    edges = [(0, 1), (0, 4), (0, 5), (1, 2),
             (1, 3), (2, 4), (2, 5)]

    # Compute uncovered-edge flags: e = (not x_u) and (not x_v).
    for ancilla, (u, v) in zip(edge_ancillas, edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], ancilla)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Compute "at least two vertices are excluded" into threshold_ancilla.
    # Its ANF, in terms z_i = not x_i, is the XOR of all even-degree
    # monomials of degrees 2, 4, and 6.
    for degree in (2, 4, 6):
        for subset in itertools.combinations(problem_qubits, degree):
            for qubit in subset:
                qc.x(qubit)
            qc.mcx(list(subset), threshold_ancilla)
            for qubit in reversed(subset):
                qc.x(qubit)

    # Convert zero-valued uncovered-edge flags to positive controls.
    for ancilla in edge_ancillas:
        qc.x(ancilla)

    # Phase flip iff all edges are covered and the cover has size at most 4.
    qc.h(phase_ancilla)
    qc.mcx(edge_ancillas + [threshold_ancilla], phase_ancilla)
    qc.h(phase_ancilla)

    for ancilla in reversed(edge_ancillas):
        qc.x(ancilla)

    # Uncompute the cardinality predicate.
    for degree in (6, 4, 2):
        for subset in reversed(list(itertools.combinations(problem_qubits, degree))):
            for qubit in subset:
                qc.x(qubit)
            qc.mcx(list(subset), threshold_ancilla)
            for qubit in reversed(subset):
                qc.x(qubit)

    # Uncompute the uncovered-edge flags.
    for ancilla, (u, v) in reversed(list(zip(edge_ancillas, edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], ancilla)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
