```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s = problem_qubits
    a0, a1, a2 = ancilla_qubits[:3]

    # Compute occurrence flags for "101" at offsets 0, 1, and 2.
    for offset, target in ((0, a0), (1, a1), (2, a2)):
        qc.x(s[offset + 1])
        qc.mcx([s[offset], s[offset + 1], s[offset + 2]], target)
        qc.x(s[offset + 1])

    # Apply (-1)^(a0 OR a1 OR a2).
    # Over GF(2): OR = a0 + a1 + a2 + a0*a1 + a0*a2 + a1*a2 + a0*a1*a2.
    qc.z(a0)
    qc.z(a1)
    qc.z(a2)
    qc.cz(a0, a1)
    qc.cz(a0, a2)
    qc.cz(a1, a2)
    qc.h(a2)
    qc.mcx([a0, a1], a2)
    qc.h(a2)

    # Uncompute occurrence flags.
    for offset, target in ((2, a2), (1, a1), (0, a0)):
        qc.x(s[offset + 1])
        qc.mcx([s[offset], s[offset + 1], s[offset + 2]], target)
        qc.x(s[offset + 1])
```
