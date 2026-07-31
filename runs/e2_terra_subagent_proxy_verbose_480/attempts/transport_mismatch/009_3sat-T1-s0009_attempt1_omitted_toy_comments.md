```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The formula simplifies to (x0 == x1), independent of x2.
    # Z(x0) Z(x1) applies -1 exactly when x0 != x1.
    qc.z(problem_qubits[0])
    qc.z(problem_qubits[1])
```
