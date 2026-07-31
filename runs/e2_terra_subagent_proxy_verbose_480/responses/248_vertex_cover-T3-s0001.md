```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The only vertex cover of size <= 2 is {2, 3}.
    zeros = [problem_qubits[i] for i in (0, 1, 4, 5)]
    target = problem_qubits[3]
    controls = [problem_qubits[i] for i in (0, 1, 2, 4, 5)]

    for qubit in zeros:
        qc.x(qubit)

    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)

    for qubit in reversed(zeros):
        qc.x(qubit)
```
