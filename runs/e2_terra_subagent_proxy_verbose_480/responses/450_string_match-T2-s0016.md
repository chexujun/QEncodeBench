```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s = problem_qubits
    m0, m1, m2, flag = ancilla_qubits

    # Compute matches for offsets 0, 1, and 2.
    qc.x(s[2])
    qc.x(s[4])
    qc.mcx([s[0], s[2], s[3], s[4]], m0)
    qc.x(s[4])
    qc.x(s[2])

    qc.x(s[3])
    qc.x(s[5])
    qc.mcx([s[1], s[3], s[4], s[5]], m1)
    qc.x(s[5])
    qc.x(s[3])

    qc.x(s[4])
    qc.x(s[6])
    qc.mcx([s[2], s[4], s[5], s[6]], m2)
    qc.x(s[6])
    qc.x(s[4])

    # Reversibly compute m0 OR m1 OR m2 into flag.
    qc.cx(m0, flag)
    qc.cx(m1, flag)
    qc.cx(m2, flag)
    qc.ccx(m0, m1, flag)
    qc.ccx(m0, m2, flag)
    qc.ccx(m1, m2, flag)
    qc.mcx([m0, m1, m2], flag)

    qc.z(flag)

    # Uncompute the OR.
    qc.mcx([m0, m1, m2], flag)
    qc.ccx(m1, m2, flag)
    qc.ccx(m0, m2, flag)
    qc.ccx(m0, m1, flag)
    qc.cx(m2, flag)
    qc.cx(m1, flag)
    qc.cx(m0, flag)

    # Uncompute matches.
    qc.x(s[4])
    qc.x(s[6])
    qc.mcx([s[2], s[4], s[5], s[6]], m2)
    qc.x(s[6])
    qc.x(s[4])

    qc.x(s[3])
    qc.x(s[5])
    qc.mcx([s[1], s[3], s[4], s[5]], m1)
    qc.x(s[5])
    qc.x(s[3])

    qc.x(s[2])
    qc.x(s[4])
    qc.mcx([s[0], s[2], s[3], s[4]], m0)
    qc.x(s[4])
    qc.x(s[2])
```
