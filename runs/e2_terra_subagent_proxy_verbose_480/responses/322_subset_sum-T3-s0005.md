```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    acc = ancilla_qubits
    n = 5
    values = [13, 4, 4, 2, 6]

    # Exact QFT, with acc[0] representing the least-significant bit.
    for j in range(n - 1, -1, -1):
        qc.h(acc[j])
        for k in range(j - 1, -1, -1):
            qc.cp(math.pi / (2 ** (j - k)), acc[j], acc[k])
    for j in range(n // 2):
        qc.swap(acc[j], acc[n - 1 - j])

    # Controlled additions into the Fourier-basis accumulator, modulo 32.
    for control, value in zip(problem_qubits, values):
        for bit in range(n):
            angle = 2 * math.pi * value / (2 ** (n - bit))
            qc.cp(angle, control, acc[bit])

    # Phase-flip exactly when the accumulated sum is 27 = 11011_2.
    qc.x(acc[2])
    qc.h(acc[4])
    qc.mcx(acc[:4], acc[4])
    qc.h(acc[4])
    qc.x(acc[2])

    # Inverse controlled additions.
    for control, value in reversed(list(zip(problem_qubits, values))):
        for bit in range(n - 1, -1, -1):
            angle = -2 * math.pi * value / (2 ** (n - bit))
            qc.cp(angle, control, acc[bit])

    # Inverse QFT.
    for j in range(n // 2):
        qc.swap(acc[j], acc[n - 1 - j])
    for j in range(n):
        for k in range(j):
            qc.cp(-math.pi / (2 ** (j - k)), acc[j], acc[k])
        qc.h(acc[j])
```
