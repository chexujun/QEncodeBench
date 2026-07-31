```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1 = problem_qubits
    equal_a, flag = ancilla_qubits[:2]

    # Compute whether the first free cell decodes to 0:
    # a0 == a1, since codes 00 and 11 both decode to 0.
    qc.cx(a0, equal_a)
    qc.cx(a1, equal_a)
    qc.x(equal_a)

    # Make b0 a positive control for the required value-2 code 10.
    qc.x(b0)

    # Mark iff: first cell is 0, second cell is 2 (b0=0, b1=1).
    qc.mcx([equal_a, b0, b1], flag)
    qc.z(flag)
    qc.mcx([equal_a, b0, b1], flag)

    qc.x(b0)

    # Uncompute equality test.
    qc.x(equal_a)
    qc.cx(a1, equal_a)
    qc.cx(a0, equal_a)
```
