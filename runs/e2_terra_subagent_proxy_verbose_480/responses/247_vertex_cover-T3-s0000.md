```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]
) -> None:
    q = problem_qubits
    fail = ancilla_qubits[:3]
    count = ancilla_qubits[3:6]
    flag = ancilla_qubits[6]

    # With vertex 1 absent, all other vertices must be present to cover its
    # incident edges, yielding size 5.  Thus a valid assignment has q[1] = 1.
    # The remaining coverage clauses are (0|4), (2|5), and (3|4).
    clauses = [(0, 4), (2, 5), (3, 4)]

    # Compute uncovered-clause indicators: fail = (~u) & (~v).
    for (u, v), target in zip(clauses, fail):
        qc.x(q[u])
        qc.x(q[v])
        qc.ccx(q[u], q[v], target)
        qc.x(q[v])
        qc.x(q[u])

    # Reversibly count selected vertices other than vertex 1 in a 3-bit
    # register.  The high bit is 0 exactly when this count is at most 3.
    counted_vertices = [q[0], q[2], q[3], q[4], q[5]]
    for vertex in counted_vertices:
        qc.mcx([vertex, count[0], count[1]], count[2])
        qc.ccx(vertex, count[0], count[1])
        qc.cx(vertex, count[0])

    # Compute q1 AND no failed clauses AND (count <= 3) into flag.
    for target in fail:
        qc.x(target)
    qc.x(count[2])
    qc.mcx([q[1], *fail, count[2]], flag)
    qc.x(count[2])
    for target in reversed(fail):
        qc.x(target)

    qc.z(flag)

    # Uncompute the flag.
    for target in fail:
        qc.x(target)
    qc.x(count[2])
    qc.mcx([q[1], *fail, count[2]], flag)
    qc.x(count[2])
    for target in reversed(fail):
        qc.x(target)

    # Uncompute the population count.
    for vertex in reversed(counted_vertices):
        qc.cx(vertex, count[0])
        qc.ccx(vertex, count[0], count[1])
        qc.mcx([vertex, count[0], count[1]], count[2])

    # Uncompute uncovered-clause indicators.
    for (u, v), target in reversed(list(zip(clauses, fail))):
        qc.x(q[u])
        qc.x(q[v])
        qc.ccx(q[u], q[v], target)
        qc.x(q[v])
        qc.x(q[u])
```
