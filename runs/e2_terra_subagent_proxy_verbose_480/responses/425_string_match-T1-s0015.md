```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flag, work = ancilla_qubits

    # Convert the required 0 bits of pattern "01010" into 1-controls.
    for i in (0, 2, 4):
        qc.x(problem_qubits[i])

    qc.mcx(problem_qubits, flag, ancilla_qubits=[work], mode="recursion")
    qc.z(flag)
    qc.mcx(problem_qubits, flag, ancilla_qubits=[work], mode="recursion")

    for i in (0, 2, 4):
        qc.x(problem_qubits[i])
```
