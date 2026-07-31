```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    equal_b = ancilla_qubits[0]
    flag = ancilla_qubits[1]

    # Compute whether cell b decodes to 0: b0 == b1.
    qc.cx(b0, equal_b)
    qc.cx(b1, equal_b)
    qc.x(equal_b)

    # Convert required zero-valued literal bits to positive controls.
    qc.x(a0)  # a = 2 requires a0 = 0, a1 = 1
    qc.x(c1)  # c = 1 requires c0 = 1, c1 = 0

    # Mark iff a=2, b decodes to 0, and c=1.
    controls = [a0, a1, c0, c1, equal_b]
    qc.mcx(controls, flag)
    qc.z(flag)
    qc.mcx(controls, flag)

    qc.x(c1)
    qc.x(a0)

    # Uncompute the decoded-zero test.
    qc.x(equal_b)
    qc.cx(b1, equal_b)
    qc.cx(b0, equal_b)
```
