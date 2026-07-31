```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    parity, flag = ancilla_qubits[:2]
    work = ancilla_qubits[2:5]

    # For covers of size <= 2, the predicate reduces to:
    # x4 AND (x0 XOR x2) AND NOT x1 AND NOT x3.
    qc.cx(x0, parity)
    qc.cx(x2, parity)

    qc.x(x1)
    qc.x(x3)
    controls = [x4, parity, x1, x3]
    qc.mcx(controls, flag, ancilla_qubits=work, mode="v-chain")
    qc.z(flag)
    qc.mcx(controls, flag, ancilla_qubits=work, mode="v-chain")
    qc.x(x3)
    qc.x(x1)

    qc.cx(x2, parity)
    qc.cx(x0, parity)
```
