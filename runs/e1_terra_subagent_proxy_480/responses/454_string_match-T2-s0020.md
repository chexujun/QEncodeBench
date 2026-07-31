```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    target = problem_qubits[-1]
    controls = problem_qubits[:-1]

    for bits in ("1010100", "1010101", "0101010", "1101010"):
        zeros = [qubit for qubit, bit in zip(problem_qubits, bits) if bit == "0"]
        for qubit in zeros:
            qc.x(qubit)
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
        for qubit in reversed(zeros):
            qc.x(qubit)
```
