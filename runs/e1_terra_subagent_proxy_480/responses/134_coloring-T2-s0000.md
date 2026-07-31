```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4)]
    flags = ancilla_qubits[:5]
    for flag, (u, v) in zip(flags, edges):
        qc.cx(problem_qubits[2 * u], flag)
        qc.cx(problem_qubits[2 * u + 1], flag)
        qc.cx(problem_qubits[2 * v], flag)
        qc.cx(problem_qubits[2 * v + 1], flag)
    qc.mcp(pi, flags[:-1], flags[-1])
    for flag, (u, v) in reversed(list(zip(flags, edges))):
        qc.cx(problem_qubits[2 * v + 1], flag)
        qc.cx(problem_qubits[2 * v], flag)
        qc.cx(problem_qubits[2 * u + 1], flag)
        qc.cx(problem_qubits[2 * u], flag)
```
