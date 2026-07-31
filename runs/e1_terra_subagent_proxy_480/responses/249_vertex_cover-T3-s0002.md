```python
from math import pi
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edges = ((0, 1), (0, 2), (0, 3), (0, 5),
             (2, 3), (2, 4), (3, 5), (4, 5))

    for value in range(64):
        bits = [(value >> i) & 1 for i in range(6)]
        is_cover = all(bits[u] or bits[v] for u, v in edges)
        if is_cover and sum(bits) <= 4:
            zero_qubits = [
                problem_qubits[i] for i, bit in enumerate(bits) if bit == 0
            ]
            qc.x(zero_qubits)
            qc.mcp(pi, problem_qubits[:-1], problem_qubits[-1])
            qc.x(zero_qubits)
```
