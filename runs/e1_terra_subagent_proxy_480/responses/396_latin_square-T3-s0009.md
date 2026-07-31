```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    target = ancilla_qubits[0]
    fixed_zero = [problem_qubits[2], problem_qubits[7]]
    variable_pairs = [
        (problem_qubits[0], problem_qubits[1]),
        (problem_qubits[4], problem_qubits[5]),
    ]

    for first_equal in (0, 1):
        for second_equal in (0, 1):
            zero_controls = fixed_zero[:]
            if first_equal == 0:
                zero_controls.extend(variable_pairs[0])
            if second_equal == 0:
                zero_controls.extend(variable_pairs[1])

            for qubit in zero_controls:
                qc.x(qubit)

            qc.mcx(problem_qubits, target)

            for qubit in reversed(zero_controls):
                qc.x(qubit)
```
