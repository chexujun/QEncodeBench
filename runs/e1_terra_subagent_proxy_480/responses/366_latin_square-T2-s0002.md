```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1 = problem_qubits[0], problem_qubits[1]
    b0, b1 = problem_qubits[2], problem_qubits[3]
    c0, c1 = problem_qubits[4], problem_qubits[5]

    equal_a = ancilla_qubits[0]
    phase = ancilla_qubits[1]
    work = ancilla_qubits[2:5]

    # equal_a = 1 precisely when the first cell decodes to 0:
    # its two code bits are equal (00 or 11).
    qc.x(equal_a)
    qc.cx(a0, equal_a)
    qc.cx(a1, equal_a)

    # Convert required zero low bits of cells B and C into positive controls.
    qc.x(b0)
    qc.x(c0)

    # Prepare |-> for phase kickback.
    qc.x(phase)
    qc.h(phase)

    # Mark iff A decodes to 0, B is 2, and C is 2.
    qc.mcx([equal_a, b0, b1, c0, c1], phase,
           ancilla_qubits=work, mode="v-chain")

    # Undo phase-kickback preparation and predicate computation.
    qc.h(phase)
    qc.x(phase)

    qc.x(c0)
    qc.x(b0)

    qc.cx(a1, equal_a)
    qc.cx(a0, equal_a)
    qc.x(equal_a)
```
