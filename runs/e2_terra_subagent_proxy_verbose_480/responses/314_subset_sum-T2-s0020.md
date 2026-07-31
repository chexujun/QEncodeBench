```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits

    # The equation 9(x0 + x1 + x2) + 7x3 = 27 holds exactly when
    # x0 = x1 = x2 = 1 and x3 = 0.
    qc.x(q3)
    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)
    qc.x(q3)
```
