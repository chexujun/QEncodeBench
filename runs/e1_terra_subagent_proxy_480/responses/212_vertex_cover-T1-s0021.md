```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for extra in (-1, 0, 2, 3):
        bits = [0, 1, 0, 0]
        if extra != -1:
            bits[extra] = 1
        for i, bit in enumerate(bits):
            if bit == 0:
                qc.x(problem_qubits[i])
        qc.h(problem_qubits[0])
        qc.mcx(problem_qubits[1:], problem_qubits[0])
        qc.h(problem_qubits[0])
        for i, bit in enumerate(bits):
            if bit == 0:
                qc.x(problem_qubits[i])
```
