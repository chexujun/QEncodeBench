```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits

    qc.x(q[2])
    qc.h(q[4])
    qc.mcx([q[0], q[1], q[2], q[3]], q[4])
    qc.h(q[4])
    qc.x(q[2])

    qc.x(q[3])
    qc.h(q[5])
    qc.mcx([q[1], q[2], q[3], q[4]], q[5])
    qc.h(q[5])
    qc.x(q[3])
```
