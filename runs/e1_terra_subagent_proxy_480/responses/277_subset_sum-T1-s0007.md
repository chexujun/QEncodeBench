```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2 = problem_qubits
    parity = ancilla_qubits[0]

    qc.cx(q0, parity)
    qc.cx(q1, parity)
    qc.x(q2)
    qc.cz(parity, q2)
    qc.x(q2)
    qc.cx(q1, parity)
    qc.cx(q0, parity)
```
