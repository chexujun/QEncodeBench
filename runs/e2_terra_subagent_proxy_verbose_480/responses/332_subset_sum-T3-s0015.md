```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    total = ancilla_qubits[:6]  # Little-endian reversible sum register.

    def controlled_add_power(control: int, bit: int) -> None:
        # Add 2**bit to `total` iff control is 1.
        for target_bit in range(len(total) - 1, bit, -1):
            qc.mcx([control] + total[:target_bit], total[target_bit])
        qc.cx(control, total[bit])

    def controlled_add_constant(control: int, value: int) -> None:
        for bit in range(len(total)):
            if (value >> bit) & 1:
                controlled_add_power(control, bit)

    values = [8, 7, 11, 2, 14]

    # Compute the selected-elements sum modulo 64.
    for qubit, value in zip(problem_qubits, values):
        controlled_add_constant(qubit, value)

    # Apply -1 precisely when the sum register equals 18 (binary 010010).
    target = 18
    for bit, qubit in enumerate(total):
        if ((target >> bit) & 1) == 0:
            qc.x(qubit)

    qc.h(total[-1])
    qc.mcx(total[:-1], total[-1])
    qc.h(total[-1])

    for bit, qubit in enumerate(total):
        if ((target >> bit) & 1) == 0:
            qc.x(qubit)

    # Uncompute the sum register.
    for qubit, value in reversed(list(zip(problem_qubits, values))):
        for bit in reversed(range(len(total))):
            if (value >> bit) & 1:
                qc.cx(qubit, total[bit])
                for target_bit in range(bit + 1, len(total)):
                    qc.mcx([qubit] + total[:target_bit], total[target_bit])
```
