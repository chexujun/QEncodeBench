```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3 = problem_qubits
    flag = ancilla_qubits[0]

    qc.x(x1)
    qc.x(x2)
    qc.x(x3)

    qc.mcx([x0, x1, x2, x3], flag)
    qc.z(flag)
    qc.mcx([x0, x1, x2, x3], flag)

    qc.x(x3)
    qc.x(x2)
    qc.x(x1)
```
