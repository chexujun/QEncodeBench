```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3, q4, q5 = problem_qubits
    eq0, eq2, flag = ancilla_qubits[:3]

    qc.cx(q0, eq0)
    qc.cx(q1, eq0)
    qc.cx(q4, eq2)
    qc.cx(q5, eq2)

    qc.x(eq0)
    qc.x(eq2)
    qc.x(q2)
    qc.mcx([eq0, eq2, q2, q3], flag)
    qc.z(flag)
    qc.mcx([eq0, eq2, q2, q3], flag)
    qc.x(q2)
    qc.x(eq2)
    qc.x(eq0)

    qc.cx(q5, eq2)
    qc.cx(q4, eq2)
    qc.cx(q1, eq0)
    qc.cx(q0, eq0)
```
