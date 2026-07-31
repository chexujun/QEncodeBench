```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for i in (0, 1, 3, 5, 6, 7):
        qc.x(problem_qubits[i])
    qc.mcx(problem_qubits, ancilla_qubits[0])
    for i in (0, 1, 3, 5, 6, 7):
        qc.x(problem_qubits[i])
```
