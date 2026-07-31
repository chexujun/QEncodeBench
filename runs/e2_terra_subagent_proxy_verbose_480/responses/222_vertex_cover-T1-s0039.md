```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    e02, e12, e13, too_many = ancilla_qubits[:4]

    # Compute the three edge-covered predicates.
    qc.cx(q0, e02)
    qc.cx(q2, e02)
    qc.ccx(q0, q2, e02)

    qc.cx(q1, e12)
    qc.cx(q2, e12)
    qc.ccx(q1, q2, e12)

    qc.cx(q1, e13)
    qc.cx(q3, e13)
    qc.ccx(q1, q3, e13)

    # Compute too_many = 1 iff the Hamming weight is at least 3.
    # ANF: e3(x0,x1,x2,x3) XOR x0*x1*x2*x3.
    qc.mcx([q0, q1, q2], too_many)
    qc.mcx([q0, q1, q3], too_many)
    qc.mcx([q0, q2, q3], too_many)
    qc.mcx([q1, q2, q3], too_many)
    qc.mcx([q0, q1, q2, q3], too_many)

    # Mark states where all edges are covered and too_many == 0.
    qc.x(too_many)
    qc.mcp(pi, [e02, e12, e13], too_many)
    qc.x(too_many)

    # Uncompute the size predicate.
    qc.mcx([q0, q1, q2, q3], too_many)
    qc.mcx([q1, q2, q3], too_many)
    qc.mcx([q0, q2, q3], too_many)
    qc.mcx([q0, q1, q3], too_many)
    qc.mcx([q0, q1, q2], too_many)

    # Uncompute the edge predicates.
    qc.ccx(q1, q3, e13)
    qc.cx(q3, e13)
    qc.cx(q1, e13)

    qc.ccx(q1, q2, e12)
    qc.cx(q2, e12)
    qc.cx(q1, e12)

    qc.ccx(q0, q2, e02)
    qc.cx(q2, e02)
    qc.cx(q0, e02)
```
