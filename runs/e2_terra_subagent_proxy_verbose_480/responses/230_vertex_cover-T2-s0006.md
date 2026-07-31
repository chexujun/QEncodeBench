```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4 = problem_qubits
    triangle_ok, edge_ok, too_large, predicate = ancilla_qubits[:4]

    # triangle_ok = 1 iff at least two of vertices 0, 1, and 4 are selected.
    qc.ccx(q0, q1, triangle_ok)
    qc.ccx(q0, q4, triangle_ok)
    qc.ccx(q1, q4, triangle_ok)

    # edge_ok = q2 OR q3.
    qc.cx(q2, edge_ok)
    qc.cx(q3, edge_ok)
    qc.ccx(q2, q3, edge_ok)

    # too_large = 1 iff the Hamming weight of the five problem bits is >= 4.
    # For five bits, threshold(weight >= 4) is the XOR of all five
    # degree-four monomials.
    qc.mcx([q1, q2, q3, q4], too_large)
    qc.mcx([q0, q2, q3, q4], too_large)
    qc.mcx([q0, q1, q3, q4], too_large)
    qc.mcx([q0, q1, q2, q4], too_large)
    qc.mcx([q0, q1, q2, q3], too_large)

    # predicate = triangle_ok AND edge_ok AND NOT too_large.
    qc.x(too_large)
    qc.mcx([triangle_ok, edge_ok, too_large], predicate)
    qc.z(predicate)
    qc.mcx([triangle_ok, edge_ok, too_large], predicate)
    qc.x(too_large)

    # Uncompute too_large.
    qc.mcx([q0, q1, q2, q3], too_large)
    qc.mcx([q0, q1, q2, q4], too_large)
    qc.mcx([q0, q1, q3, q4], too_large)
    qc.mcx([q0, q2, q3, q4], too_large)
    qc.mcx([q1, q2, q3, q4], too_large)

    # Uncompute edge_ok.
    qc.ccx(q2, q3, edge_ok)
    qc.cx(q3, edge_ok)
    qc.cx(q2, edge_ok)

    # Uncompute triangle_ok.
    qc.ccx(q1, q4, triangle_ok)
    qc.ccx(q0, q4, triangle_ok)
    qc.ccx(q0, q1, triangle_ok)
```
