```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 4), (3, 4)]
    edge_flags = ancilla_qubits[:6]
    size_flag = ancilla_qubits[6]

    triples = []
    for i in range(5):
        for j in range(i + 1, 5):
            for k in range(j + 1, 5):
                triples.append([problem_qubits[i],
                                problem_qubits[j],
                                problem_qubits[k]])

    quadruples = []
    for i in range(5):
        for j in range(i + 1, 5):
            for k in range(j + 1, 5):
                for ell in range(k + 1, 5):
                    quadruples.append([problem_qubits[i],
                                       problem_qubits[j],
                                       problem_qubits[k],
                                       problem_qubits[ell]])

    # Compute [Hamming weight <= 2] in algebraic normal form:
    # 1 XOR (all degree-3 monomials) XOR (all degree-4 monomials).
    qc.x(size_flag)
    for controls in triples:
        qc.mcx(controls, size_flag)
    for controls in quadruples:
        qc.mcx(controls, size_flag)

    # Each edge flag is 1 exactly when that edge is uncovered.
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Phase flip iff every edge flag is 0 and the size condition is true.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcp(math.pi, edge_flags, size_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute uncovered-edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Uncompute the size predicate.
    for controls in reversed(quadruples):
        qc.mcx(controls, size_flag)
    for controls in reversed(triples):
        qc.mcx(controls, size_flag)
    qc.x(size_flag)
```
