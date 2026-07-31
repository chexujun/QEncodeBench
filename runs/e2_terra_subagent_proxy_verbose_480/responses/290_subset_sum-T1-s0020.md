```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits

    qc.x(x0)
    qc.h(x2)
    qc.mcx([x0, x1], x2)
    qc.h(x2)
    qc.x(x0)
```
