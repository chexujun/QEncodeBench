```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The only subset totaling 4 is {a[3]}:
    # x3 = 1 and x0 = x1 = x2 = x4 = 0.
    controls = problem_qubits
    flag = ancilla_qubits[0]

    for i in (0, 1, 2, 4):
        qc.x(problem_qubits[i])

    qc.mcx(controls, flag)
    qc.z(flag)
    qc.mcx(controls, flag)

    for i in (4, 2, 1, 0):
        qc.x(problem_qubits[i])
```
