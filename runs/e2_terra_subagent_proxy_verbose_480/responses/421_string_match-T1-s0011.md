```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q1, q2, q3 = problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a, b = ancilla_qubits

    qc.x(q3)
    qc.ccx(q1, q2, a)
    qc.ccx(a, q3, b)
    qc.z(b)
    qc.ccx(a, q3, b)
    qc.ccx(q1, q2, a)
    qc.x(q3)
```
