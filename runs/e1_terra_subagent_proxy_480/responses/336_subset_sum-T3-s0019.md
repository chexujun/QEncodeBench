```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    for q in problem_qubits[:4]:
        qc.x(q)
    qc.h(problem_qubits[4])
    qc.mcx(problem_qubits[:4], problem_qubits[4])
    qc.h(problem_qubits[4])
    for q in problem_qubits[:4]:
        qc.x(q)
```
