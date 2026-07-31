```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    p0, p1, p2, valid = ancilla_qubits[:4]
    lo = [problem_qubits[0], problem_qubits[2], problem_qubits[4]]
    hi = [problem_qubits[1], problem_qubits[3], problem_qubits[5]]
    ps = [p0, p1, p2]

    # p[v] is 1 exactly when vertex v has color 1 or 2.
    for low, high, parity in zip(lo, hi, ps):
        qc.cx(low, parity)
        qc.cx(high, parity)

    # All three colors differ iff exactly one p[v] is zero and the low bits
    # of the other two vertices differ.
    for zero_vertex, first, second in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
        qc.x(ps[zero_vertex])
        qc.cx(lo[first], lo[second])
        qc.mcx([p0, p1, p2, lo[second]], valid)
        qc.cx(lo[first], lo[second])
        qc.x(ps[zero_vertex])

    qc.z(valid)

    # Uncompute the validity predicate.
    for zero_vertex, first, second in reversed(
        ((0, 1, 2), (1, 0, 2), (2, 0, 1))
    ):
        qc.x(ps[zero_vertex])
        qc.cx(lo[first], lo[second])
        qc.mcx([p0, p1, p2, lo[second]], valid)
        qc.cx(lo[first], lo[second])
        qc.x(ps[zero_vertex])

    # Uncompute color-class parity bits.
    for low, high, parity in reversed(list(zip(lo, hi, ps))):
        qc.cx(high, parity)
        qc.cx(low, parity)
```
