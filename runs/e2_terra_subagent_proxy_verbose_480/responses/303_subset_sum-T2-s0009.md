```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Four ancillas store the selected-value sum modulo 16.  This is
    # sufficient because all possible sums lie in [0, 26], so only 12
    # is congruent to 12 modulo 16.
    total = ancilla_qubits[:4]
    flag = ancilla_qubits[4]

    def controlled_increment(control):
        for bit in range(3, 0, -1):
            qc.mcx([control] + total[:bit], total[bit])
        qc.cx(control, total[0])

    def controlled_decrement(control):
        qc.cx(control, total[0])
        for bit in range(1, 4):
            qc.mcx([control] + total[:bit], total[bit])

    values = [6, 5, 9, 6]

    # Compute the subset sum modulo 16.
    for qubit, value in zip(problem_qubits, values):
        for _ in range(value):
            controlled_increment(qubit)

    # Compute total == 12 into flag, apply the phase, and uncompute.
    qc.x(total[0])
    qc.x(total[1])
    qc.mcx(total, flag)
    qc.z(flag)
    qc.mcx(total, flag)
    qc.x(total[1])
    qc.x(total[0])

    # Uncompute the subset sum.
    for qubit, value in reversed(list(zip(problem_qubits, values))):
        for _ in range(value):
            controlled_decrement(qubit)
```
