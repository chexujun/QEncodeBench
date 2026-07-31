```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    acc = ancilla_qubits  # little-endian 4-bit accumulator

    def controlled_add_power(control, bit, inverse=False):
        if not inverse:
            for target_bit in range(3, bit, -1):
                qc.mcx([control] + acc[bit:target_bit], acc[target_bit])
            qc.cx(control, acc[bit])
        else:
            qc.cx(control, acc[bit])
            for target_bit in range(bit + 1, 4):
                qc.mcx([control] + acc[bit:target_bit], acc[target_bit])

    additions = [
        (problem_qubits[0], [0, 2]),  # add 5
        (problem_qubits[1], [1]),     # add 2
        (problem_qubits[2], [0, 1]),  # add 3
    ]

    # Compute selected-subset sum into the accumulator modulo 16.
    for control, bits in additions:
        for bit in bits:
            controlled_add_power(control, bit)

    # Phase flip iff accumulator equals 5 (binary 0101).
    qc.x(acc[1])
    qc.x(acc[3])
    qc.h(acc[3])
    qc.mcx([acc[0], acc[1], acc[2]], acc[3])
    qc.h(acc[3])
    qc.x(acc[3])
    qc.x(acc[1])

    # Uncompute the accumulator.
    for control, bits in reversed(additions):
        for bit in reversed(bits):
            controlled_add_power(control, bit, inverse=True)
```
