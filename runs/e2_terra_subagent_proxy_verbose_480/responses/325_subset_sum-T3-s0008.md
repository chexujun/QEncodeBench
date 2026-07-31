```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    acc = ancilla_qubits[:6]  # Little-endian 6-bit accumulator.
    operations = []

    def controlled_increment(control: int, start_bit: int) -> None:
        # Add 2**start_bit modulo 64 when control is 1.
        for target_bit in range(5, start_bit, -1):
            controls = [control] + acc[start_bit:target_bit]
            target = acc[target_bit]
            qc.mcx(controls, target)
            operations.append((controls, target))

        qc.cx(control, acc[start_bit])
        operations.append(([control], acc[start_bit]))

    # Compute 4*x0 + 10*x1 + 10*x2 + 3*x3 + 14*x4.
    for input_bit, value in zip(problem_qubits, (4, 10, 10, 3, 14)):
        bit = 0
        while value:
            if value & 1:
                controlled_increment(input_bit, bit)
            value >>= 1
            bit += 1

    # Phase flip precisely when accumulator equals 17 = 0b010001.
    for bit in (1, 2, 3, 5):
        qc.x(acc[bit])

    qc.h(acc[5])
    qc.mcx(acc[:5], acc[5])
    qc.h(acc[5])

    for bit in (5, 3, 2, 1):
        qc.x(acc[bit])

    # Uncompute the accumulator.
    for controls, target in reversed(operations):
        if len(controls) == 1:
            qc.cx(controls[0], target)
        else:
            qc.mcx(controls, target)
```
