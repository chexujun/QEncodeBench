```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edges = ((0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (3, 4))
    target = problem_qubits[-1]
    controls = problem_qubits[:-1]

    for mask in range(1 << 6):
        bits = [(mask >> i) & 1 for i in range(6)]
        if sum(bits) <= 4 and all(bits[u] or bits[v] for u, v in edges):
            flipped = [problem_qubits[i] for i, bit in enumerate(bits) if not bit]
            for qubit in flipped:
                qc.x(qubit)
            qc.mcp(math.pi, controls, target)
            for qubit in reversed(flipped):
                qc.x(qubit)
```
