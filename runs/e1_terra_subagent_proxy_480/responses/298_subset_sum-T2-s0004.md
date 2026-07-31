```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for mask in (0b0110, 0b1001):
        for i, qubit in enumerate(problem_qubits):
            if not (mask >> i) & 1:
                qc.x(qubit)
        qc.h(problem_qubits[-1])
        qc.mcx(problem_qubits[:-1], problem_qubits[-1])
        qc.h(problem_qubits[-1])
        for i, qubit in enumerate(problem_qubits):
            if not (mask >> i) & 1:
                qc.x(qubit)
```
