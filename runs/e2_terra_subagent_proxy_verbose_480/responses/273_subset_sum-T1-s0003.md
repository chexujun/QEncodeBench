```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # 5*x0 + x1 + 3*x2 = 8 iff x0 = 1 and x2 = 1.
    # Implement a CCZ, using x2 as the target.
    q0, _, q2 = problem_qubits
    qc.h(q2)
    qc.ccx(q0, problem_qubits[1], q2)  # temporarily used below only for structure
    qc.ccx(q0, problem_qubits[1], q2)
    qc.ccx(q0, q2, problem_qubits[1])
    qc.ccx(q0, q2, problem_qubits[1])
    qc.ccx(q0, q2, problem_qubits[1])
    qc.h(q2)
```
