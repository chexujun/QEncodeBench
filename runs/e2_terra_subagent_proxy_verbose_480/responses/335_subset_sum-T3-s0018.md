```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    sums = ancilla_qubits[:6]
    values = [15, 11, 9, 13, 7]
    operations = []

    # Compute the selected-element sum modulo 64. Since the maximum possible
    # sum is 55, this representation is exact for every input.
    for select, value in zip(problem_qubits, values):
        for shift in range(6):
            if (value >> shift) & 1:
                # Controlled increment of sums[shift:6], processed from the
                # most significant bit downward so controls see the old value.
                for target in range(5, shift, -1):
                    controls = [select] + sums[shift:target]
                    qc.mcx(controls, sums[target])
                    operations.append(("mcx", controls, sums[target]))
                qc.cx(select, sums[shift])
                operations.append(("cx", select, sums[shift]))

    # Mark sum == 40, whose six-bit little-endian representation is 101000.
    for bit in (0, 1, 2, 4):
        qc.x(sums[bit])
    qc.h(sums[5])
    qc.mcx(sums[:5], sums[5])
    qc.h(sums[5])
    for bit in (0, 1, 2, 4):
        qc.x(sums[bit])

    # Uncompute the sum and return every ancilla to |0>.
    for operation in reversed(operations):
        if operation[0] == "cx":
            qc.cx(operation[1], operation[2])
        else:
            qc.mcx(operation[1], operation[2])
```
