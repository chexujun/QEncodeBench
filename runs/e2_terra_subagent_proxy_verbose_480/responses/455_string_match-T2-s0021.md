```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flag, work0, work1 = ancilla_qubits

    def mark_five_literals(first_four, fifth, zero_controls):
        for q in zero_controls:
            qc.x(q)

        qc.mcx(first_four, flag, ancilla_qubits=[work0, work1], mode="v-chain")
        qc.cz(flag, fifth)
        qc.mcx(first_four, flag, ancilla_qubits=[work0, work1], mode="v-chain")

        for q in reversed(zero_controls):
            qc.x(q)

    # Offset 0: s0 s1 s2 s3 s4 = 1 1 0 1 1
    mark_five_literals(
        [problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]],
        problem_qubits[4],
        [problem_qubits[2]],
    )

    # Offset 1: s1 s2 s3 s4 s5 = 1 1 0 1 1
    mark_five_literals(
        [problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]],
        problem_qubits[5],
        [problem_qubits[3]],
    )
```
