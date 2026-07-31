```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    majority, parity, flag = ancilla_qubits[:3]

    # For the three elements equal to 6:
    # majority = 1 when at least two are selected.
    qc.ccx(x0, x3, majority)
    qc.ccx(x0, x4, majority)
    qc.ccx(x3, x4, majority)

    # parity = x0 XOR x3 XOR x4.
    # Thus majority=1 and parity=0 iff exactly two are selected.
    qc.cx(x0, parity)
    qc.cx(x3, parity)
    qc.cx(x4, parity)

    # The sum is 24 iff x1=0, x2=1, and exactly two 6s are selected.
    qc.x(x1)
    qc.x(parity)
    qc.mcx([x1, x2, majority, parity], flag)
    qc.z(flag)
    qc.mcx([x1, x2, majority, parity], flag)
    qc.x(parity)
    qc.x(x1)

    # Uncompute all work ancillas.
    qc.cx(x4, parity)
    qc.cx(x3, parity)
    qc.cx(x0, parity)

    qc.ccx(x3, x4, majority)
    qc.ccx(x0, x4, majority)
    qc.ccx(x0, x3, majority)
```
