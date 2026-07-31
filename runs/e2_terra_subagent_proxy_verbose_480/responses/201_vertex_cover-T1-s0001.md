```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    e01, e02, e23, too_many, phase = ancilla_qubits[:5]

    # Compute edge-covered flags: xa OR xb = xa XOR xb XOR (xa AND xb).
    def compute_or(a, b, target):
        qc.cx(a, target)
        qc.cx(b, target)
        qc.ccx(a, b, target)

    def uncompute_or(a, b, target):
        qc.ccx(a, b, target)
        qc.cx(b, target)
        qc.cx(a, target)

    compute_or(x0, x1, e01)
    compute_or(x0, x2, e02)
    compute_or(x2, x3, e23)

    # Compute whether the Hamming weight is at least 3.
    # XOR of all 3-way products is 1 for weight 3; adding x0*x1*x2*x3
    # also makes it 1 for weight 4.
    qc.ccx(x0, x1, too_many)
    qc.ccx(x0, x2, too_many)
    qc.ccx(x0, x3, too_many)
    qc.ccx(x1, x2, too_many)
    qc.ccx(x1, x3, too_many)
    qc.ccx(x2, x3, too_many)
    qc.mcx([x0, x1, x2, x3], too_many)

    # Convert "too_many" into the required weight <= 2 condition.
    qc.x(too_many)

    # Phase kickback for: all edges covered AND weight <= 2.
    qc.x(phase)
    qc.h(phase)
    qc.mcx([e01, e02, e23, too_many], phase)
    qc.h(phase)
    qc.x(phase)

    qc.x(too_many)

    # Uncompute the size condition.
    qc.mcx([x0, x1, x2, x3], too_many)
    qc.ccx(x2, x3, too_many)
    qc.ccx(x1, x3, too_many)
    qc.ccx(x1, x2, too_many)
    qc.ccx(x0, x3, too_many)
    qc.ccx(x0, x2, too_many)
    qc.ccx(x0, x1, too_many)

    # Uncompute edge-covered flags.
    uncompute_or(x2, x3, e23)
    uncompute_or(x0, x2, e02)
    uncompute_or(x0, x1, e01)
```
