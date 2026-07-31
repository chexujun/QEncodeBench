```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    a = ancilla_qubits[0]

    qc.cx(q0, a)
    qc.cx(q1, a)

    qc.x(a)
    qc.x(q3)
    qc.mcp(3.141592653589793, [a, q2, q3])

    qc.x(q3)
    qc.x(a)

    qc.cx(q1, a)
    qc.cx(q0, a)
```
