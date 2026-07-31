```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a_or = ancilla_qubits

    def compute_match(offset: int, target: int) -> None:
        # Pattern 0101: invert controls for the required zero bits.
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 2])
        qc.mcx(problem_qubits[offset:offset + 4], target)
        qc.x(problem_qubits[offset + 2])
        qc.x(problem_qubits[offset])

    compute_match(0, a0)
    compute_match(1, a1)

    # a_or = a0 OR a1 = a0 XOR a1 XOR (a0 AND a1)
    qc.cx(a0, a_or)
    qc.cx(a1, a_or)
    qc.ccx(a0, a1, a_or)

    qc.z(a_or)

    qc.ccx(a0, a1, a_or)
    qc.cx(a1, a_or)
    qc.cx(a0, a_or)

    compute_match(1, a1)
    compute_match(0, a0)
```
