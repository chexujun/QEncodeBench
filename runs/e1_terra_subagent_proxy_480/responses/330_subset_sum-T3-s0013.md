```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    for selected in ((1, 1, 0, 1, 0), (1, 0, 0, 1, 1), (0, 1, 1, 1, 1)):
        zero_controls = [q for q, bit in zip(problem_qubits, selected) if not bit]
        for q in zero_controls:
            qc.x(q)
        qc.mcx(problem_qubits, target)
        for q in zero_controls:
            qc.x(q)
```
