```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The sole subset totaling 11 is {a[4]}: x4=1 and x0=x1=x2=x3=0.
    controls = list(problem_qubits)
    flag = ancilla_qubits[0]
    work = list(ancilla_qubits[1:4])

    for qubit in problem_qubits[:4]:
        qc.x(qubit)

    qc.mcx(controls, flag, ancilla_qubits=work, mode="v-chain")
    qc.z(flag)
    qc.mcx(controls, flag, ancilla_qubits=work, mode="v-chain")

    for qubit in reversed(problem_qubits[:4]):
        qc.x(qubit)
```
