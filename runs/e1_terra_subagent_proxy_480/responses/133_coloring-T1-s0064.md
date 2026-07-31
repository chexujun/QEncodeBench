```python
from itertools import product
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edges = ((0, 1), (0, 3), (1, 3), (2, 3))

    for encoding in product(range(4), repeat=4):
        colors = tuple(0 if value == 3 else value for value in encoding)
        if any(colors[u] == colors[v] for u, v in edges):
            continue

        bits = []
        for value in encoding:
            bits.extend((value & 1, (value >> 1) & 1))

        zero_qubits = [
            problem_qubits[index]
            for index, bit in enumerate(bits)
            if bit == 0
        ]
        for qubit in zero_qubits:
            qc.x(qubit)

        qc.mcp(pi, problem_qubits[:-1], problem_qubits[-1])

        for qubit in reversed(zero_qubits):
            qc.x(qubit)
```
