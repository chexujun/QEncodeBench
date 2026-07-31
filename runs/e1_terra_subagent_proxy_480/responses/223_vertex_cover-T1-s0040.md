```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    valid_covers = (
        (0, 1, 0, 1),  # {1, 3}
        (0, 1, 1, 0),  # {1, 2}
        (1, 0, 0, 1),  # {0, 3}
    )

    for pattern in valid_covers:
        zero_controls = [
            problem_qubits[i] for i, bit in enumerate(pattern) if bit == 0
        ]
        for qubit in zero_controls:
            qc.x(qubit)
        qc.mcx(problem_qubits, target)
        for qubit in reversed(zero_controls):
            qc.x(qubit)
```
