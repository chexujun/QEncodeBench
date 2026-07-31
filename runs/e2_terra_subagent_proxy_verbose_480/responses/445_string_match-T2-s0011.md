```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s0, s1, s2, s3, s4, _ = problem_qubits
    a0, a1, a2, _ = ancilla_qubits

    # Compute matches at offsets 0, 1, and 2.
    qc.x(s1)
    qc.mcx([s0, s1, s2], a0)
    qc.x(s1)

    qc.x(s2)
    qc.mcx([s1, s2, s3], a1)
    qc.x(s2)

    qc.x(s3)
    qc.mcx([s2, s3, s4], a2)
    qc.x(s3)

    # A and B cannot overlap; B and C cannot overlap.
    # Only A and C can overlap, so OR(A,B,C) = A xor B xor C xor (A and C).
    qc.z(a0)
    qc.z(a1)
    qc.z(a2)
    qc.cz(a0, a2)

    # Uncompute.
    qc.x(s3)
    qc.mcx([s2, s3, s4], a2)
    qc.x(s3)

    qc.x(s2)
    qc.mcx([s1, s2, s3], a1)
    qc.x(s2)

    qc.x(s1)
    qc.mcx([s0, s1, s2], a0)
    qc.x(s1)
```
