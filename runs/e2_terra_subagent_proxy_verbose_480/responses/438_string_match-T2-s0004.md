```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flag = ancilla_qubits[0]
    work = ancilla_qubits[1]

    # Offset 0: s[0:6] == 001010
    for i in (0, 1, 3, 5):
        qc.x(problem_qubits[i])
    qc.mcx(problem_qubits[0:6], flag, ancilla_qubits=[work], mode="recursion")
    qc.z(flag)
    qc.mcx(problem_qubits[0:6], flag, ancilla_qubits=[work], mode="recursion")
    for i in (5, 3, 1, 0):
        qc.x(problem_qubits[i])

    # Offset 1: s[1:7] == 001010
    for i in (1, 2, 4, 6):
        qc.x(problem_qubits[i])
    qc.mcx(problem_qubits[1:7], flag, ancilla_qubits=[work], mode="recursion")
    qc.z(flag)
    qc.mcx(problem_qubits[1:7], flag, ancilla_qubits=[work], mode="recursion")
    for i in (6, 4, 2, 1):
        qc.x(problem_qubits[i])
```
