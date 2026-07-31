```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[5])
    qc.mcp(3.141592653589793, problem_qubits[:5], problem_qubits[5])
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
```
