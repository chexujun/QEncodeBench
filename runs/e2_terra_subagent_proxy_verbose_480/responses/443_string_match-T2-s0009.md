```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s = problem_qubits
    a0, a1, a2 = ancilla_qubits[:3]

    def compute_matches():
        qc.x(s[4])
        qc.mcx([s[0], s[1], s[3], s[4]], a0)

        qc.x(s[5])
        qc.mcx([s[1], s[2], s[4], s[5]], a1)

        qc.x(s[6])
        qc.mcx([s[2], s[3], s[5], s[6]], a2)

    def uncompute_matches():
        qc.mcx([s[2], s[3], s[5], s[6]], a2)
        qc.x(s[6])

        qc.mcx([s[1], s[2], s[4], s[5]], a1)
        qc.x(s[5])

        qc.mcx([s[0], s[1], s[3], s[4]], a0)
        qc.x(s[4])

    compute_matches()

    qc.z(a0)
    qc.z(a1)
    qc.z(a2)
    qc.cz(a0, a1)
    qc.cz(a0, a2)
    qc.cz(a1, a2)
    qc.h(a2)
    qc.mcx([a0, a1], a2)
    qc.h(a2)

    uncompute_matches()
```
