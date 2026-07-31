```python
from qiskit import QuantumCircuit
from math import pi

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    for solution in ((0, 2, 4), (1, 2, 4)):
        selected = set(solution)
        for i, qubit in enumerate(problem_qubits):
            if i not in selected:
                qc.x(qubit)
        qc.mcp(pi, problem_qubits[:-1], problem_qubits[-1])
        for i, qubit in enumerate(problem_qubits):
            if i not in selected:
                qc.x(qubit)
```
