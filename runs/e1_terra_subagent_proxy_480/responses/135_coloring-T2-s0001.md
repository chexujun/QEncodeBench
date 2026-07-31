```python
from itertools import product
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    encoding = {0: (0, 0), 1: (0, 1), 2: (1, 0)}
    for colors in product(range(3), repeat=4):
        if all(colors[u] != colors[v] for u, v in ((0, 2), (0, 3), (1, 2), (1, 3), (2, 3))):
            bits = [bit for color in colors for bit in encoding[color]]
            for qubit, bit in zip(q, bits):
                if bit == 0:
                    qc.x(qubit)
            qc.h(q[-1])
            qc.mcx(q[:-1], q[-1])
            qc.h(q[-1])
            for qubit, bit in zip(q, bits):
                if bit == 0:
                    qc.x(qubit)
```
