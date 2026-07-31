```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Compute the selected-element sum into a five-bit little-endian register.
    # A controlled increment is applied once for every unit in each weight.
    # This is reversible modular arithmetic; the largest possible sum is 20.
    acc = ancilla_qubits[:5]
    weights = (7, 5, 6, 2)

    def controlled_increment(control: int) -> None:
        # Add one modulo 2^5, conditioned on `control`.
        for bit in range(len(acc) - 1, 0, -1):
            qc.mcx([control, *acc[:bit]], acc[bit])
        qc.cx(control, acc[0])

    def controlled_decrement(control: int) -> None:
        # Inverse of controlled_increment.
        qc.cx(control, acc[0])
        for bit in range(1, len(acc)):
            qc.mcx([control, *acc[:bit]], acc[bit])

    for select, weight in zip(problem_qubits, weights):
        for _ in range(weight):
            controlled_increment(select)

    # Apply a phase iff the accumulator equals 6 (binary 00110).
    for bit in (acc[0], acc[3], acc[4]):
        qc.x(bit)
    qc.h(acc[4])
    qc.mcx(acc[:4], acc[4])
    qc.h(acc[4])
    for bit in (acc[0], acc[3], acc[4]):
        qc.x(bit)

    # Uncompute the sum register.
    for select, weight in reversed(list(zip(problem_qubits, weights))):
        for _ in range(weight):
            controlled_decrement(select)
```
