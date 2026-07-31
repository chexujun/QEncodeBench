```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    left_xor, right_xor, predicate = ancilla_qubits[:3]

    # A valid cover must contain vertex 2 and exactly one vertex from
    # each of the pairs {0, 1} and {3, 4}.
    qc.cx(x0, left_xor)
    qc.cx(x1, left_xor)
    qc.cx(x3, right_xor)
    qc.cx(x4, right_xor)

    qc.mcx([x2, left_xor, right_xor], predicate)
    qc.z(predicate)
    qc.mcx([x2, left_xor, right_xor], predicate)

    qc.cx(x4, right_xor)
    qc.cx(x3, right_xor)
    qc.cx(x1, left_xor)
    qc.cx(x0, left_xor)
```
