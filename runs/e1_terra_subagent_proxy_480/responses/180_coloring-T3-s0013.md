```python
from itertools import product
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edges = ((0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4),
             (2, 3), (3, 4))

    for codes in product(range(4), repeat=5):
        colors = [code if code < 3 else 0 for code in codes]
        if not all(colors[u] != colors[v] for u, v in edges):
            continue

        bits = []
        for code in codes:
            bits.extend((code & 1, (code >> 1) & 1))

        for qubit, bit in zip(problem_qubits, bits):
            if bit == 0:
                qc.x(qubit)

        target = problem_qubits[0]
        qc.h(target)
        qc.mcx(problem_qubits[1:], target)
        qc.h(target)

        for qubit, bit in zip(problem_qubits, bits):
            if bit == 0:
                qc.x(qubit)
```
