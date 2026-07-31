```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    qc.x(problem_qubits[2])
    qc.h(problem_qubits[3])
    qc.mcx(problem_qubits[:3], problem_qubits[3])
    qc.h(problem_qubits[3])
    qc.x(problem_qubits[2])
```
