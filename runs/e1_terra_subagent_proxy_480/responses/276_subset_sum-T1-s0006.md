```python
import qiskit

def build_oracle(
    qc: qiskit.QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2 = problem_qubits
    work = ancilla_qubits[0]

    qc.x(q0)
    qc.x(q1)
    qc.ccx(q0, q1, work)
    qc.cz(work, q2)
    qc.ccx(q0, q1, work)
    qc.x(q1)
    qc.x(q0)
```
