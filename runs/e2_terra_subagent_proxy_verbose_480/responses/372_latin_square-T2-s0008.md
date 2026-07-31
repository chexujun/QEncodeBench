```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    eq_a, eq_b, flag = ancilla_qubits[:3]

    # eq_a/equ_b hold XORs; they are 0 exactly when the decoded value is 0.
    qc.cx(a0, eq_a)
    qc.cx(a1, eq_a)
    qc.cx(b0, eq_b)
    qc.cx(b1, eq_b)

    # Convert required zero-controls to one-controls.
    qc.x(eq_a)
    qc.x(eq_b)
    qc.x(c1)  # c must decode to 1: c0=1, c1=0

    qc.mcx([eq_a, eq_b, c0, c1], flag)
    qc.z(flag)
    qc.mcx([eq_a, eq_b, c0, c1], flag)

    qc.x(c1)
    qc.x(eq_b)
    qc.x(eq_a)

    qc.cx(b1, eq_b)
    qc.cx(b0, eq_b)
    qc.cx(a1, eq_a)
    qc.cx(a0, eq_a)
```
