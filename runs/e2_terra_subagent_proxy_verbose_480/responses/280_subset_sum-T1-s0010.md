```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2 = problem_qubits

    # Mark exactly x = 010: select only the element of value 6.
    qc.x(q0)
    qc.x(q2)
    qc.h(q1)
    qc.ccx(q0, q2, q1)
    qc.h(q1)
    qc.x(q2)
    qc.x(q0)
```
