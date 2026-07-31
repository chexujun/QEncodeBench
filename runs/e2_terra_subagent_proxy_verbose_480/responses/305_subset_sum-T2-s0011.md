```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    acc = ancilla_qubits[:5]
    n = 5
    values = [7, 7, 10, 4]

    def qft_no_swaps():
        for j in range(n):
            qc.h(acc[j])
            for k in range(j + 1, n):
                qc.cp(math.pi / (2 ** (k - j)), acc[k], acc[j])

    def iqft_no_swaps():
        for j in range(n - 1, -1, -1):
            for k in range(n - 1, j, -1):
                qc.cp(-math.pi / (2 ** (k - j)), acc[k], acc[j])
            qc.h(acc[j])

    def controlled_add(value, control, sign=1):
        for j in range(n):
            angle = sign * 2.0 * math.pi * value / (2 ** (n - j))
            qc.cp(angle, control, acc[j])

    # Compute the selected-subset sum into the five-qubit accumulator.
    qft_no_swaps()
    for bit, value in zip(problem_qubits, values):
        controlled_add(value, bit)
    iqft_no_swaps()

    # Apply -1 precisely when the accumulator is 17 (binary 10001).
    for j in (1, 2, 3):
        qc.x(acc[j])
    qc.h(acc[4])
    qc.mcx(acc[:4], acc[4])
    qc.h(acc[4])
    for j in (1, 2, 3):
        qc.x(acc[j])

    # Uncompute the accumulator.
    qft_no_swaps()
    for bit, value in zip(problem_qubits, values):
        controlled_add(value, bit, sign=-1)
    iqft_no_swaps()
```
