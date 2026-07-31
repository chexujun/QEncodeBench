```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    xor_11, xor_6, term_zero, term_one, flag = ancilla_qubits[:5]

    # xor_11 = x0 XOR x3; xor_6 = x1 XOR x4
    qc.cx(x0, xor_11)
    qc.cx(x3, xor_11)
    qc.cx(x1, xor_6)
    qc.cx(x4, xor_6)

    # term_zero = (not x2) AND x0 AND x3 AND (not x1) AND (not x4)
    qc.x(x1)
    qc.x(x2)
    qc.x(x4)
    qc.mcx([x0, x3, x1, x2, x4], term_zero)
    qc.x(x4)
    qc.x(x2)
    qc.x(x1)

    # term_one = x2 AND (x0 XOR x3) AND (x1 XOR x4)
    qc.mcx([x2, xor_11, xor_6], term_one)

    # The two terms are disjoint, so their XOR is their OR.
    qc.cx(term_zero, flag)
    qc.cx(term_one, flag)
    qc.z(flag)
    qc.cx(term_one, flag)
    qc.cx(term_zero, flag)

    # Uncompute all work qubits.
    qc.mcx([x2, xor_11, xor_6], term_one)

    qc.x(x1)
    qc.x(x2)
    qc.x(x4)
    qc.mcx([x0, x3, x1, x2, x4], term_zero)
    qc.x(x4)
    qc.x(x2)
    qc.x(x1)

    qc.cx(x4, xor_6)
    qc.cx(x1, xor_6)
    qc.cx(x3, xor_11)
    qc.cx(x0, xor_11)
```
