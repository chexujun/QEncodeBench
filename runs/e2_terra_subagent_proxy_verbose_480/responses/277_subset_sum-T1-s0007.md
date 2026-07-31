```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    parity, flag = ancilla_qubits[:2]

    qc.cx(x0, parity)
    qc.cx(x1, parity)

    qc.x(x2)
    qc.ccx(parity, x2, flag)
    qc.z(flag)
    qc.ccx(parity, x2, flag)
    qc.x(x2)

    qc.cx(x1, parity)
    qc.cx(x0, parity)
```
