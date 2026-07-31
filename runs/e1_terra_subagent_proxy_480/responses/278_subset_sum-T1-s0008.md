```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    parity = ancilla_qubits[0]

    qc.cx(x1, parity)
    qc.cx(x2, parity)
    qc.x(x0)
    qc.cz(x0, parity)
    qc.x(x0)
    qc.cx(x2, parity)
    qc.cx(x1, parity)
```
