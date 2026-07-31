```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4)]
    nonedges = [(0, 2), (0, 4), (1, 4), (3, 4)]

    edge_flags = ancilla_qubits[:6]
    phase_flag = ancilla_qubits[6]
    mcx_work = ancilla_qubits[7]

    # edge_flags[j] = 1 exactly when edge j is uncovered.
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Turn edge_flags == 0 into positive controls.
    for flag in edge_flags:
        qc.x(flag)

    # Under the vertex-cover condition, excluded vertices form an independent
    # set. This graph has no independent set of size three, so a cover has
    # size <= 3 exactly when one of these four nonedge pairs is excluded.
    controls_prefix = list(edge_flags)
    for u, v in nonedges:
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])

        controls = controls_prefix + [problem_qubits[u], problem_qubits[v]]
        qc.mcx(controls, phase_flag,
               ancilla_qubits=[mcx_work], mode="recursion")
        qc.z(phase_flag)
        qc.mcx(controls, phase_flag,
               ancilla_qubits=[mcx_work], mode="recursion")

        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute all uncovered-edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
