```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    low0, high0, low1, _ = problem_qubits

    qc.x(low0)
    qc.x(low1)
    qc.h(high0)
    qc.mcx([low0, low1], high0)
    qc.h(high0)
    qc.x(low1)
    qc.x(low0)
```
