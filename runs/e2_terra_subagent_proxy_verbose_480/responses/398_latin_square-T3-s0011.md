```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    eq_first = ancilla_qubits[0]
    eq_last = ancilla_qubits[1]
    work = ancilla_qubits[2:5]

    # Compute whether the two value-0 cells use 00 or 11.
    qc.cx(problem_qubits[0], eq_first)
    qc.cx(problem_qubits[1], eq_first)
    qc.x(eq_first)

    qc.cx(problem_qubits[6], eq_last)
    qc.cx(problem_qubits[7], eq_last)
    qc.x(eq_last)

    # The two value-2 cells must each have code 10.
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])

    # Phase flip iff all six conditions hold.
    controls = [
        eq_first,
        problem_qubits[2],
        problem_qubits[3],
        problem_qubits[4],
        problem_qubits[5],
    ]
    qc.h(eq_last)
    qc.mcx(controls, eq_last, ancilla_qubits=work, mode="v-chain")
    qc.h(eq_last)

    # Uncompute.
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])

    qc.x(eq_last)
    qc.cx(problem_qubits[7], eq_last)
    qc.cx(problem_qubits[6], eq_last)

    qc.x(eq_first)
    qc.cx(problem_qubits[1], eq_first)
    qc.cx(problem_qubits[0], eq_first)
```
