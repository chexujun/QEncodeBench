```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Convert the required 0-bits into 1-controls.
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])

    # Multi-controlled Z: phase-flip exactly when all six literals match.
    target = problem_qubits[5]
    qc.h(target)
    qc.mcx(problem_qubits[:5], target)
    qc.h(target)

    # Restore the problem register.
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[0])
```
