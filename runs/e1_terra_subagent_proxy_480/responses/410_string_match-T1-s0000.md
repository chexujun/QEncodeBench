```python
from math import pi
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.mcp(
        pi,
        [problem_qubits[0], problem_qubits[1], problem_qubits[4]],
        problem_qubits[5],
    )
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[1])
```
