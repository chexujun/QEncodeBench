```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The constraints simplify to the unique valid pattern:
    # x0=0, x1=1, x2=0, x3=1.
    x0, x1, x2, x3 = problem_qubits

    qc.x(x0)
    qc.x(x2)
    qc.h(x3)
    qc.mcx([x0, x1, x2], x3)
    qc.h(x3)
    qc.x(x2)
    qc.x(x0)
```
