```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Convert the desired string 100101 into all ones.
    for index in (1, 2, 4):
        qc.x(problem_qubits[index])

    # Apply a phase flip iff all six problem qubits are 1.
    qc.h(problem_qubits[5])
    qc.mcx(problem_qubits[:5], problem_qubits[5])
    qc.h(problem_qubits[5])

    # Restore the original computational-basis encoding.
    for index in (4, 2, 1):
        qc.x(problem_qubits[index])
```
