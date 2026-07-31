```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]

    for code0 in ((0, 0), (1, 1)):
        for code2 in ((0, 0), (1, 1)):
            required = [
                code0[0], code0[1],
                1, 0,
                code2[0], code2[1],
                1, 0,
            ]
            zero_controls = [
                qubit for qubit, value in zip(problem_qubits, required)
                if value == 0
            ]

            for qubit in zero_controls:
                qc.x(qubit)
            qc.mcx(problem_qubits, target)
            for qubit in reversed(zero_controls):
                qc.x(qubit)
```
