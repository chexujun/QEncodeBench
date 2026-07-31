```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    qc.x([problem_qubits[0], problem_qubits[1], problem_qubits[3], problem_qubits[4]])
    qc.h(problem_qubits[2])
    qc.mcx(
        [problem_qubits[0], problem_qubits[1], problem_qubits[3], problem_qubits[4]],
        problem_qubits[2],
    )
    qc.h(problem_qubits[2])
    qc.x([problem_qubits[0], problem_qubits[1], problem_qubits[3], problem_qubits[4]])
```
