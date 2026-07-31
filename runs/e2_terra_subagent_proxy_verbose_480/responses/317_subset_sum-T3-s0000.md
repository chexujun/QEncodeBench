```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    values = (7, 10, 5, 3, 9)
    accumulator = ancilla_qubits[:6]
    n = len(accumulator)
    modulus = 1 << n

    def qft() -> None:
        for j in reversed(range(n)):
            qc.h(accumulator[j])
            for k in reversed(range(j)):
                qc.cp(pi / (1 << (j - k)), accumulator[j], accumulator[k])
        for j in range(n // 2):
            qc.swap(accumulator[j], accumulator[n - 1 - j])

    def inverse_qft() -> None:
        for j in reversed(range(n // 2)):
            qc.swap(accumulator[j], accumulator[n - 1 - j])
        for j in range(n):
            for k in range(j):
                qc.cp(-pi / (1 << (j - k)), accumulator[j], accumulator[k])
            qc.h(accumulator[j])

    def add_selected_values(sign: int) -> None:
        for control, value in zip(problem_qubits, values):
            for bit, target in enumerate(accumulator):
                angle = sign * 2 * pi * value * (1 << bit) / modulus
                qc.cp(angle, control, target)

    qft()
    add_selected_values(1)
    inverse_qft()

    # Mark accumulator value 16 = 0b010000.
    for bit in (0, 1, 2, 3, 5):
        qc.x(accumulator[bit])
    qc.h(accumulator[5])
    qc.mcx(accumulator[:5], accumulator[5])
    qc.h(accumulator[5])
    for bit in (0, 1, 2, 3, 5):
        qc.x(accumulator[bit])

    qft()
    add_selected_values(-1)
    inverse_qft()
```
