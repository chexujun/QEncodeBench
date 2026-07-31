```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    xor_24 = ancilla_qubits[0]
    flag = ancilla_qubits[1]

    # Under the size-at-most-2 constraint, a cover must contain vertex 0
    # and exactly one of vertices 2 and 4, while excluding vertices 1 and 3.
    qc.cx(x2, xor_24)
    qc.cx(x4, xor_24)

    qc.x(x1)
    qc.x(x3)
    qc.mcx([x0, xor_24, x1, x3], flag)
    qc.z(flag)
    qc.mcx([x0, xor_24, x1, x3], flag)
    qc.x(x3)
    qc.x(x1)

    qc.cx(x4, xor_24)
    qc.cx(x2, xor_24)
```
