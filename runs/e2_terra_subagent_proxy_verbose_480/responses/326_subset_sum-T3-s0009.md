```python
import math

from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    parity, majority, flag = ancilla_qubits[:3]

    # Compute parity of the three elements having value 3.
    qc.cx(x0, parity)
    qc.cx(x2, parity)
    qc.cx(x4, parity)

    # Compute their majority bit: x0*x2 XOR x0*x4 XOR x2*x4.
    qc.ccx(x0, x2, majority)
    qc.ccx(x0, x4, majority)
    qc.ccx(x2, x4, majority)

    # A sum of 6 requires exactly two of the 3s, and neither 14 nor 13.
    qc.x(parity)
    qc.x(x1)
    qc.x(x3)
    qc.mcx([majority, parity, x1, x3], flag)
    qc.z(flag)
    qc.mcx([majority, parity, x1, x3], flag)
    qc.x(x3)
    qc.x(x1)
    qc.x(parity)

    # Uncompute ancillas.
    qc.ccx(x2, x4, majority)
    qc.ccx(x0, x4, majority)
    qc.ccx(x0, x2, majority)

    qc.cx(x4, parity)
    qc.cx(x2, parity)
    qc.cx(x0, parity)
```
