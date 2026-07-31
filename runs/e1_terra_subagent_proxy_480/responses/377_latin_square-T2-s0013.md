```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q = problem_qubits
    zero_controls = [q[0], q[2], q[3], q[5]]

    qc.x(zero_controls)
    qc.h(q[4])
    qc.mcx([q[0], q[1], q[2], q[3], q[5]], q[4])
    qc.h(q[4])
    qc.x(zero_controls)
```
