```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Any cover of size <= 2 must contain vertex 0: otherwise vertices
    # 1, 2, and 4 are all required. Once 0 is included, covering both
    # (2,3) and (3,4) with only one remaining vertex forces vertex 3.
    # Thus the unique satisfying assignment is x0=x3=1 and x1=x2=x4=0.
    flag = ancilla_qubits[0]

    for i in (1, 2, 4):
        qc.x(problem_qubits[i])

    qc.mcx([problem_qubits[i] for i in range(5)], flag)
    qc.z(flag)
    qc.mcx([problem_qubits[i] for i in range(5)], flag)

    for i in (4, 2, 1):
        qc.x(problem_qubits[i])
```
