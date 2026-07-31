```python
from qiskit import QuantumCircuit
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    qc.x(q[2]); qc.x(q[3])
    qc.mcp(3.141592653589793, [q[0], q[1], q[2]], q[3])
    qc.x(q[3]); qc.x(q[2])
    qc.x(q[0]); qc.x(q[3])
    qc.mcp(3.141592653589793, [q[0], q[1], q[2]], q[3])
    qc.x(q[3]); qc.x(q[0])
```
