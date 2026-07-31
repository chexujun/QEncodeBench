```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    b00, b01, b10, b11 = problem_qubits
    flag = ancilla_qubits[0]

    # Both free cells must decode to value 2, i.e. each code is 10.
    qc.x(b00)
    qc.x(b10)
    qc.mcx([b00, b01, b10, b11], flag)
    qc.z(flag)
    qc.mcx([b00, b01, b10, b11], flag)
    qc.x(b10)
    qc.x(b00)
```
