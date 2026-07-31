```python
from qiskit import QuantumCircuit


def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = ((0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4))
    flags = ancilla_qubits[:7]
    scratch = ancilla_qubits[7]

    def toggle_on_pattern(controls, pattern, target):
        for qubit, value in zip(controls, pattern):
            if value == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, value in zip(controls, pattern):
            if value == 0:
                qc.x(qubit)

    def compute_conflict(a, b, c, d, target):
        qc.cx(a, scratch)
        qc.cx(c, scratch)
        qc.cx(scratch, target)
        qc.cx(b, target)
        qc.cx(d, target)
        toggle_on_pattern((scratch, a, b, d), (1, 1, 0, 1), target)
        toggle_on_pattern((scratch, a, b, d), (1, 0, 1, 0), target)
        qc.cx(c, scratch)
        qc.cx(a, scratch)

    for (u, v), flag in zip(edges, flags):
        compute_conflict(problem_qubits[2*u], problem_qubits[2*u+1], problem_qubits[2*v], problem_qubits[2*v+1], flag)
    qc.h(scratch)
    qc.mcx(flags, scratch)
    qc.h(scratch)
    for (u, v), flag in reversed(tuple(zip(edges, flags))):
        compute_conflict(problem_qubits[2*u], problem_qubits[2*u+1], problem_qubits[2*v], problem_qubits[2*v+1], flag)
```
