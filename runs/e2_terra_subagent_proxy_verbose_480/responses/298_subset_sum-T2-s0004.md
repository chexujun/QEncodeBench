```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    acc = ancilla_qubits[:4]
    n = 4
    modulus = 1 << n

    def qft():
        for j in range(n - 1, -1, -1):
            qc.h(acc[j])
            for k in range(j - 1, -1, -1):
                qc.cp(math.pi / (1 << (j - k)), acc[j], acc[k])
        for j in range(n // 2):
            qc.swap(acc[j], acc[n - 1 - j])

    def iqft():
        for j in range(n // 2):
            qc.swap(acc[j], acc[n - 1 - j])
        for j in range(n):
            for k in range(j):
                qc.cp(-math.pi / (1 << (j - k)), acc[j], acc[k])
            qc.h(acc[j])

    def controlled_add(control, value):
        for j in range(n):
            angle = 2 * math.pi * value * (1 << j) / modulus
            qc.cp(angle, control, acc[j])

    qft()
    for bit, value in enumerate([1, 4, 4, 7]):
        controlled_add(problem_qubits[bit], value)
    iqft()

    qc.x(acc[0])
    qc.x(acc[1])
    qc.x(acc[2])
    qc.h(acc[3])
    qc.mcx(acc[:3], acc[3])
    qc.h(acc[3])
    qc.x(acc[2])
    qc.x(acc[1])
    qc.x(acc[0])

    qft()
    for bit, value in reversed(list(enumerate([1, 4, 4, 7]))):
        controlled_add(problem_qubits[bit], -value)
    iqft()
```
