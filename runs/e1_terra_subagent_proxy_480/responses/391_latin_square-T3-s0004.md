```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    zero_bits = [problem_qubits[i] for i in (0, 1, 3, 6, 7)]
    qc.x(zero_bits)
    qc.mcx(problem_qubits, target)
    qc.z(target)
    qc.mcx(problem_qubits, target)
    qc.x(zero_bits)
```
