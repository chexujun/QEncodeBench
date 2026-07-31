```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    controls = problem_qubits[:4]

    for qubit in problem_qubits[:3]:
        qc.x(qubit)

    qc.mcx(controls, target)

    for qubit in problem_qubits[:3]:
        qc.x(qubit)
```
