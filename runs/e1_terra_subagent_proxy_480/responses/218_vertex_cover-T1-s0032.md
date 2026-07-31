```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for bits in ((1, 0, 1, 0), (0, 1, 0, 1), (0, 0, 1, 1)):
        for i, bit in enumerate(bits):
            if bit == 0:
                qc.x(problem_qubits[i])
        target = problem_qubits[3]
        qc.h(target)
        qc.mcx(problem_qubits[:3], target)
        qc.h(target)
        for i, bit in enumerate(bits):
            if bit == 0:
                qc.x(problem_qubits[i])
```
