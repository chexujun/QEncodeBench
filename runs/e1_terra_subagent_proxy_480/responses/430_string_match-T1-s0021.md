```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    qc.x(problem_qubits[0])
    qc.cx(problem_qubits[0], ancilla_qubits[0])
    qc.x(problem_qubits[0])
```
