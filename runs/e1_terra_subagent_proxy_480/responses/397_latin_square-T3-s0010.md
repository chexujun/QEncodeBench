```python
from qiskit import QuantumCircuit
from math import pi

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    p = problem_qubits
    for z4 in (0, 1):
        for z6 in (0, 1):
            bits = [0, 1, 1, 0, z4, z4, z6, z6]
            zeros = [p[i] for i, bit in enumerate(bits) if bit == 0]
            for qubit in zeros:
                qc.x(qubit)
            qc.mcp(pi, p[:-1], p[-1])
            for qubit in zeros:
                qc.x(qubit)
```
