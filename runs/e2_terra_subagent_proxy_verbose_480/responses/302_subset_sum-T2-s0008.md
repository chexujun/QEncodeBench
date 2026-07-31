```python
import math
from qiskit.circuit.library import QFT

def build_oracle(qc, problem_qubits, ancilla_qubits):
    acc = ancilla_qubits
    n = 5
    modulus = 1 << n
    values = [9, 8, 2, 10]

    qft = QFT(n, do_swaps=True)
    iqft = qft.inverse()

    qc.append(qft, acc)
    for selector, value in zip(problem_qubits, values):
        for bit, target in enumerate(acc):
            qc.cp(2 * math.pi * value / (1 << (bit + 1)), selector, target)
    qc.append(iqft, acc)

    # Mark accumulator value 27 = 11011 (little-endian).
    qc.x(acc[2])
    qc.h(acc[4])
    qc.mcx(acc[:4], acc[4])
    qc.h(acc[4])
    qc.x(acc[2])

    qc.append(qft, acc)
    for selector, value in reversed(list(zip(problem_qubits, values))):
        for bit, target in reversed(list(enumerate(acc))):
            qc.cp(-2 * math.pi * value / (1 << (bit + 1)), selector, target)
    qc.append(iqft, acc)
```
