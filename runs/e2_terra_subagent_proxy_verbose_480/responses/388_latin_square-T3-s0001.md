```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The fixed clues force the free-cell values to be:
    #   cell 0 = 0, cell 1 = 2, cell 2 = 0, cell 3 = 1.
    # Under the surjective decoding, a cell represents 0 exactly when
    # its two code bits are equal.
    zero_cell_0 = ancilla_qubits[0]
    zero_cell_2 = ancilla_qubits[1]

    # Compute the two equality predicates.
    qc.x(zero_cell_0)
    qc.cx(problem_qubits[0], zero_cell_0)
    qc.cx(problem_qubits[1], zero_cell_0)

    qc.x(zero_cell_2)
    qc.cx(problem_qubits[4], zero_cell_2)
    qc.cx(problem_qubits[5], zero_cell_2)

    # Convert the required zero-valued code bits into positive controls:
    # cell 1 = 10 requires b0=0, b1=1;
    # cell 3 = 01 requires b0=1, b1=0.
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[7])

    qc.mcp(
        math.pi,
        [
            zero_cell_0,
            problem_qubits[2],
            problem_qubits[3],
            zero_cell_2,
            problem_qubits[6],
        ],
        problem_qubits[7],
    )

    qc.x(problem_qubits[7])
    qc.x(problem_qubits[2])

    # Uncompute the equality predicates and restore all ancillas to |0>.
    qc.cx(problem_qubits[5], zero_cell_2)
    qc.cx(problem_qubits[4], zero_cell_2)
    qc.x(zero_cell_2)

    qc.cx(problem_qubits[1], zero_cell_0)
    qc.cx(problem_qubits[0], zero_cell_0)
    qc.x(zero_cell_0)
```
