```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    v = problem_qubits
    edge_flags = ancilla_qubits[:5]
    count_lsb = ancilla_qubits[5]
    count_msb = ancilla_qubits[6]
    phase_target = ancilla_qubits[7]

    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]

    # Compute one flag per edge: flag = v[u] OR v[w].
    for (u, w), flag in zip(edges, edge_flags):
        qc.cx(v[u], flag)
        qc.cx(v[w], flag)
        qc.ccx(v[u], v[w], flag)

    # Compute Hamming weight modulo 4 into count_lsb/count_msb.
    for qubit in v:
        qc.ccx(qubit, count_lsb, count_msb)
        qc.cx(qubit, count_lsb)

    # Any vertex cover has size at least two here.  Thus, within the
    # all-edges-covered subspace, weight <= 2 is exactly weight mod 4 == 2.
    qc.x(count_lsb)
    qc.x(phase_target)
    qc.mcp(
        math.pi,
        edge_flags + [count_lsb, count_msb],
        phase_target,
    )
    qc.x(phase_target)
    qc.x(count_lsb)

    # Uncompute the modulo-4 Hamming weight.
    for qubit in reversed(v):
        qc.cx(qubit, count_lsb)
        qc.ccx(qubit, count_lsb, count_msb)

    # Uncompute edge-coverage flags.
    for (u, w), flag in reversed(list(zip(edges, edge_flags))):
        qc.ccx(v[u], v[w], flag)
        qc.cx(v[w], flag)
        qc.cx(v[u], flag)
```
