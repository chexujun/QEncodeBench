```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    valid_patterns = (
        (0, 1, 0, 0, 1, 0, 0, 0),
        (0, 1, 1, 1, 1, 0, 0, 0),
        (0, 1, 0, 0, 1, 0, 1, 1),
        (0, 1, 1, 1, 1, 0, 1, 1),
    )
    for pattern in valid_patterns:
        zeros = [problem_qubits[i] for i, bit in enumerate(pattern) if bit == 0]
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(problem_qubits, target)
        for qubit in zeros:
            qc.x(qubit)
```
