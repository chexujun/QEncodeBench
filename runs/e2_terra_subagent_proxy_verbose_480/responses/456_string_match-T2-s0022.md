```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:3]

    def compute_match(offset: int, target: int) -> None:
        # Required substring bits are 0, 0, 1 at positions offset+1..offset+3.
        q0 = problem_qubits[offset + 1]
        q1 = problem_qubits[offset + 2]
        q2 = problem_qubits[offset + 3]
        qc.x(q0)
        qc.x(q1)
        qc.mcx([q0, q1, q2], target)
        qc.x(q1)
        qc.x(q0)

    for offset, flag in enumerate(flags):
        compute_match(offset, flag)

    # Phase for flag0 OR flag1 OR flag2, expressed in ANF.
    for flag in flags:
        qc.z(flag)
    qc.cz(flags[0], flags[1])
    qc.cz(flags[0], flags[2])
    qc.cz(flags[1], flags[2])
    qc.h(flags[2])
    qc.mcx([flags[0], flags[1]], flags[2])
    qc.h(flags[2])

    for offset, flag in reversed(list(enumerate(flags))):
        compute_match(offset, flag)
```
