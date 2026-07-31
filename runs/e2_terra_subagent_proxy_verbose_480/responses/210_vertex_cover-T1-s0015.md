```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    xor01, predicate = ancilla_qubits[:2]

    # Valid covers of size <= 2 satisfy:
    # x2 AND (NOT x3) AND (x0 XOR x1).
    qc.cx(x0, xor01)
    qc.cx(x1, xor01)

    qc.x(x3)
    qc.mcx([xor01, x2, x3], predicate)
    qc.z(predicate)
    qc.mcx([xor01, x2, x3], predicate)
    qc.x(x3)

    qc.cx(x1, xor01)
    qc.cx(x0, xor01)
```
