```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    s0, s1, s2, flag = ancilla_qubits

    # Controlled additions modulo 8 into (s2 s1 s0), little-endian.
    # Add 5*x0.
    qc.ccx(x0, s0, s1)
    qc.mcx([x0, s0, s1], s2)
    qc.cx(x0, s0)
    qc.cx(x0, s2)

    # Add 3*x1.
    qc.ccx(x1, s1, s2)
    qc.cx(x1, s1)
    qc.ccx(x1, s0, s1)
    qc.mcx([x1, s0, s1], s2)
    qc.cx(x1, s0)

    # Add 2*x2.
    qc.ccx(x2, s1, s2)
    qc.cx(x2, s1)

    # Set flag iff accumulated sum is 5 (binary 101).
    qc.x(s1)
    qc.mcx([s0, s1, s2], flag)
    qc.x(s1)
    qc.z(flag)
    qc.x(s1)
    qc.mcx([s0, s1, s2], flag)
    qc.x(s1)

    # Uncompute 2*x2.
    qc.cx(x2, s1)
    qc.ccx(x2, s1, s2)

    # Uncompute 3*x1.
    qc.cx(x1, s0)
    qc.mcx([x1, s0, s1], s2)
    qc.ccx(x1, s0, s1)
    qc.cx(x1, s1)
    qc.ccx(x1, s1, s2)

    # Uncompute 5*x0.
    qc.cx(x0, s2)
    qc.cx(x0, s0)
    qc.mcx([x0, s0, s1], s2)
    qc.ccx(x0, s0, s1)
```
