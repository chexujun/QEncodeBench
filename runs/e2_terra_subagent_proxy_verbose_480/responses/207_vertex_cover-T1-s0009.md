```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    c01, c02, c03, c23, covered, _, phase = ancilla_qubits

    # Compute the four edge-coverage clauses.
    clauses = [
        (x0, x1, c01),
        (x0, x2, c02),
        (x0, x3, c03),
        (x2, x3, c23),
    ]
    for u, v, target in clauses:
        qc.cx(u, target)
        qc.cx(v, target)
        qc.ccx(u, v, target)  # target = u OR v

    # covered = all four edges are covered.
    qc.mcx([c01, c02, c03, c23], covered)

    # Uncompute the individual clause ancillas, freeing c01, c02, c03.
    for u, v, target in reversed(clauses):
        qc.ccx(u, v, target)
        qc.cx(v, target)
        qc.cx(u, target)

    # Reuse c01, c02, c03 as a three-bit counter for Hamming weight.
    count_bits = [c01, c02, c03]
    for vertex in problem_qubits:
        qc.mcx([vertex, count_bits[0], count_bits[1]], count_bits[2])
        qc.ccx(vertex, count_bits[0], count_bits[1])
        qc.cx(vertex, count_bits[0])

    # Weight <= 2 iff count_bits[2] == 0 and not(count_bits[1] & count_bits[0]).
    qc.ccx(count_bits[0], count_bits[1], c23)
    qc.x(count_bits[2])
    qc.x(c23)
    qc.mcx([covered, count_bits[2], c23], phase)
    qc.z(phase)
    qc.mcx([covered, count_bits[2], c23], phase)
    qc.x(c23)
    qc.x(count_bits[2])
    qc.ccx(count_bits[0], count_bits[1], c23)

    # Uncompute the Hamming-weight counter.
    for vertex in reversed(problem_qubits):
        qc.cx(vertex, count_bits[0])
        qc.ccx(vertex, count_bits[0], count_bits[1])
        qc.mcx([vertex, count_bits[0], count_bits[1]], count_bits[2])

    # Uncompute the all-edges-covered flag.
    qc.mcx([c01, c02, c03, c23], covered)
```
