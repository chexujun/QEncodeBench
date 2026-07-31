```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    xnor_0 = ancilla_qubits[0]
    xnor_2 = ancilla_qubits[1]
    flag = ancilla_qubits[2]

    # Cell 0 decodes to 0 exactly when its two code bits are equal.
    qc.cx(problem_qubits[0], xnor_0)
    qc.cx(problem_qubits[1], xnor_0)
    qc.x(xnor_0)

    # Cell 2 decodes to 0 exactly when its two code bits are equal.
    qc.cx(problem_qubits[4], xnor_2)
    qc.cx(problem_qubits[5], xnor_2)
    qc.x(xnor_2)

    # Convert the required zero-valued literals to positive controls.
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[7])

    controls = [
        xnor_0,
        problem_qubits[2],
        problem_qubits[3],
        xnor_2,
        problem_qubits[6],
        problem_qubits[7],
    ]
    qc.mcx(controls, flag)
    qc.z(flag)
    qc.mcx(controls, flag)

    qc.x(problem_qubits[7])
    qc.x(problem_qubits[2])

    qc.x(xnor_2)
    qc.cx(problem_qubits[5], xnor_2)
    qc.cx(problem_qubits[4], xnor_2)

    qc.x(xnor_0)
    qc.cx(problem_qubits[1], xnor_0)
    qc.cx(problem_qubits[0], xnor_0)
```
