```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_flags = ancilla_qubits[:7]
    count = ancilla_qubits[7:10]
    edges = ((0, 3), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (3, 5))

    # Compute one flag per uncovered edge.
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly count vertices not in the cover in a three-bit counter.
    # A cover of size at most 4 has at least two zero bits.
    for q in problem_qubits:
        qc.x(q)
        qc.mcx([q, count[0], count[1]], count[2])
        qc.ccx(q, count[0], count[1])
        qc.cx(q, count[0])
        qc.x(q)

    # All edge flags must be zero; phase-mark counter values 2 through 6.
    for flag in edge_flags:
        qc.x(flag)

    for value in (2, 3, 4, 5, 6):
        for bit, wire in enumerate(count):
            if not ((value >> bit) & 1):
                qc.x(wire)

        qc.mcp(math.pi, edge_flags + [count[0], count[1]], count[2])

        for bit, wire in reversed(list(enumerate(count))):
            if not ((value >> bit) & 1):
                qc.x(wire)

    for flag in edge_flags:
        qc.x(flag)

    # Uncompute the zero-count counter.
    for q in reversed(problem_qubits):
        qc.x(q)
        qc.cx(q, count[0])
        qc.ccx(q, count[0], count[1])
        qc.mcx([q, count[0], count[1]], count[2])
        qc.x(q)

    # Uncompute uncovered-edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
