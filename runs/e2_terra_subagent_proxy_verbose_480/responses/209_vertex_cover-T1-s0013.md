```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    e03, and23, e12_e13, cover, too_large, phase = ancilla_qubits

    # Compute edge-coverage predicate:
    # (x0 OR x3) AND (x1 OR (x2 AND x3)).
    qc.cx(x0, e03)
    qc.cx(x3, e03)
    qc.ccx(x0, x3, e03)

    qc.ccx(x2, x3, and23)

    qc.cx(x1, e12_e13)
    qc.cx(and23, e12_e13)
    qc.ccx(x1, and23, e12_e13)

    qc.ccx(e03, e12_e13, cover)

    # Compute whether Hamming weight is at least 3.
    # This is e3 XOR e4, where ej is the j-th elementary
    # symmetric Boolean polynomial of the four input bits.
    qc.mcx([x0, x1, x2], too_large)
    qc.mcx([x0, x1, x3], too_large)
    qc.mcx([x0, x2, x3], too_large)
    qc.mcx([x1, x2, x3], too_large)
    qc.mcx([x0, x1, x2, x3], too_large)

    # Mark iff the cover predicate holds and weight is not too large.
    qc.x(too_large)
    qc.ccx(cover, too_large, phase)
    qc.z(phase)
    qc.ccx(cover, too_large, phase)
    qc.x(too_large)

    # Uncompute Hamming-weight predicate.
    qc.mcx([x0, x1, x2, x3], too_large)
    qc.mcx([x1, x2, x3], too_large)
    qc.mcx([x0, x2, x3], too_large)
    qc.mcx([x0, x1, x3], too_large)
    qc.mcx([x0, x1, x2], too_large)

    # Uncompute edge-coverage predicate.
    qc.ccx(e03, e12_e13, cover)

    qc.ccx(x1, and23, e12_e13)
    qc.cx(and23, e12_e13)
    qc.cx(x1, e12_e13)

    qc.ccx(x2, x3, and23)

    qc.ccx(x0, x3, e03)
    qc.cx(x3, e03)
    qc.cx(x0, e03)
```
