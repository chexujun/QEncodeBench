```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, _, _, q3, q4, _ = problem_qubits
    qc.x(q4)
    qc.h(q0)
    qc.mcx([q3, q4], q0)
    qc.h(q0)
    qc.x(q4)
```
