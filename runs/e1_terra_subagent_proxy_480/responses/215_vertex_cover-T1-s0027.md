```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    valid_assignments = (
        (1, 0, 0, 0),
        (1, 1, 0, 0),
        (1, 0, 1, 0),
        (1, 0, 0, 1),
    )

    for assignment in valid_assignments:
        zero_qubits = [
            problem_qubits[i] for i, bit in enumerate(assignment) if bit == 0
        ]
        for qubit in zero_qubits:
            qc.x(qubit)
        qc.mcp(
            3.141592653589793,
            problem_qubits[:-1],
            problem_qubits[-1],
        )
        for qubit in reversed(zero_qubits):
            qc.x(qubit)
```
