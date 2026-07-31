```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    color_bits = ((0, 0), (1, 0), (0, 1))

    for c1 in range(3):
        for c4 in range(3):
            if c1 == c4:
                continue
            remaining = next(c for c in range(3) if c != c1 and c != c4)
            colors = (remaining, c1, remaining, remaining, c4)
            bits = [bit for color in colors for bit in color_bits[color]]

            for qubit, bit in zip(problem_qubits, bits):
                if bit == 0:
                    qc.x(qubit)

            qc.h(problem_qubits[-1])
            qc.mcx(problem_qubits[:-1], problem_qubits[-1])
            qc.h(problem_qubits[-1])

            for qubit, bit in zip(problem_qubits, bits):
                if bit == 0:
                    qc.x(qubit)
```
