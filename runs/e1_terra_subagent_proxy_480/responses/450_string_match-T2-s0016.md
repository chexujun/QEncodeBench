```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for offset in range(3):
        ones = [problem_qubits[offset], problem_qubits[offset + 3]]
        zeros = [problem_qubits[offset + 2], problem_qubits[offset + 4]]

        for qubit in zeros:
            qc.x(qubit)

        qc.mcp(3.141592653589793, ones + [zeros[0]], zeros[1])

        for qubit in reversed(zeros):
            qc.x(qubit)
```
