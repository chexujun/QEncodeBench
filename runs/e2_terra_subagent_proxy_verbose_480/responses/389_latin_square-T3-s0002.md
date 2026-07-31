```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits[:4]

    # Cell (0,2) must have code 10.
    qc.x(problem_qubits[0])
    qc.ccx(problem_qubits[0], problem_qubits[1], a0)
    qc.x(problem_qubits[0])

    # Cell (1,2) must decode to 0: code 00 or 11.
    qc.cx(problem_qubits[2], a1)
    qc.cx(problem_qubits[3], a1)
    qc.x(a1)

    # Cell (2,1) must decode to 0: code 00 or 11.
    qc.cx(problem_qubits[4], a2)
    qc.cx(problem_qubits[5], a2)
    qc.x(a2)

    # Cell (2,2) must have code 01.
    qc.x(problem_qubits[7])
    qc.ccx(problem_qubits[6], problem_qubits[7], a3)
    qc.x(problem_qubits[7])

    # Apply -1 exactly when all four required cell conditions hold.
    qc.mcp(pi, [a0, a1, a2], a3)

    # Uncompute all predicate ancillas.
    qc.x(problem_qubits[7])
    qc.ccx(problem_qubits[6], problem_qubits[7], a3)
    qc.x(problem_qubits[7])

    qc.x(a2)
    qc.cx(problem_qubits[5], a2)
    qc.cx(problem_qubits[4], a2)

    qc.x(a1)
    qc.cx(problem_qubits[3], a1)
    qc.cx(problem_qubits[2], a1)

    qc.x(problem_qubits[0])
    qc.ccx(problem_qubits[0], problem_qubits[1], a0)
    qc.x(problem_qubits[0])
```
