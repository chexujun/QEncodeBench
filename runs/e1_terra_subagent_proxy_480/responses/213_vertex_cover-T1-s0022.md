```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for chosen in ({0, 1}, {0, 3}, {2, 3}):
        for i, qubit in enumerate(problem_qubits):
            if i not in chosen:
                qc.x(qubit)
        qc.h(problem_qubits[3])
        qc.mcx(problem_qubits[:3], problem_qubits[3])
        qc.h(problem_qubits[3])
        for i, qubit in enumerate(problem_qubits):
            if i not in chosen:
                qc.x(qubit)
```
