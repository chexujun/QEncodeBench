```python
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for offset in (0, 1):
        qubits = problem_qubits[offset:offset + 4]
        for index in (0, 2, 3):
            qc.x(qubits[index])
        qc.mcp(pi, qubits[:3], qubits[3])
        for index in (0, 2, 3):
            qc.x(qubits[index])
```
