```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a_match_0, a_match_1 = ancilla_qubits[:2]

    # Match "1101" at offset 0.
    qc.x(q[2])
    qc.mcx([q[0], q[1], q[2], q[3]], a_match_0)
    qc.x(q[2])

    # Match "1101" at offset 1.
    qc.x(q[3])
    qc.mcx([q[1], q[2], q[3], q[4]], a_match_1)
    qc.x(q[3])

    # Apply phase -1 iff either match flag is set.
    qc.z(a_match_0)
    qc.z(a_match_1)
    qc.cz(a_match_0, a_match_1)

    # Uncompute offset-1 match.
    qc.x(q[3])
    qc.mcx([q[1], q[2], q[3], q[4]], a_match_1)
    qc.x(q[3])

    # Uncompute offset-0 match.
    qc.x(q[2])
    qc.mcx([q[0], q[1], q[2], q[3]], a_match_0)
    qc.x(q[2])
```
