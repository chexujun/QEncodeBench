```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    acc = ancilla_qubits[:6]
    values = (13, 10, 5, 14, 3)
    n = 6

    def qft() -> None:
        for j in range(n - 1, -1, -1):
            qc.h(acc[j])
            for k in range(j - 1, -1, -1):
                qc.cp(math.pi / (1 << (j - k)), acc[j], acc[k])
        for j in range(n // 2):
            qc.swap(acc[j], acc[n - 1 - j])

    def inverse_qft() -> None:
        for j in range(n // 2):
            qc.swap(acc[j], acc[n - 1 - j])
        for j in range(n):
            for k in range(j):
                qc.cp(-math.pi / (1 << (j - k)), acc[j], acc[k])
            qc.h(acc[j])

    def fourier_add(sign: int) -> None:
        for control, value in zip(problem_qubits, values):
            for j in range(n):
                angle = sign * 2.0 * math.pi * value * (1 << j) / (1 << n)
                qc.cp(angle, control, acc[j])

    # Compute the selected-element sum modulo 64. Since the maximum possible
    # sum is 45, this is also the ordinary integer sum.
    qft()
    fourier_add(1)
    inverse_qft()

    # Apply a phase exactly when the accumulator is 37 = 0b100101.
    for j in (1, 3, 4):
        qc.x(acc[j])
    qc.h(acc[5])
    qc.mcx(acc[:5], acc[5])
    qc.h(acc[5])
    for j in (1, 3, 4):
        qc.x(acc[j])

    # Uncompute the accumulator.
    qft()
    fourier_add(-1)
    inverse_qft()
```
