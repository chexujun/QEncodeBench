```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Four equality flags (one per edge) plus a phase-kickback qubit.
    flags = ancilla_qubits[:4]
    phase = ancilla_qubits[4]

    def toggle_when_bits(controls: list[int], bits: tuple[int, ...], target: int) -> None:
        for qubit, bit in zip(controls, bits):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in zip(controls, bits):
            if bit == 0:
                qc.x(qubit)

    def toggle_equal(a0: int, a1: int, b0: int, b1: int, target: int) -> None:
        controls = [a0, a1, b0, b1]
        for bits in (
            (0, 0, 0, 0),  # 0 == 0
            (0, 0, 1, 1),  # 0 == encoded 3
            (1, 1, 0, 0),  # encoded 3 == 0
            (1, 1, 1, 1),  # encoded 3 == encoded 3
            (1, 0, 1, 0),  # 1 == 1
            (0, 1, 0, 1),  # 2 == 2
        ):
            toggle_when_bits(controls, bits, target)

    edges = ((0, 1), (0, 3), (1, 2), (2, 3))
    for flag, (u, v) in zip(flags, edges):
        toggle_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    for flag in flags:
        qc.x(flag)
    qc.x(phase)
    qc.h(phase)
    qc.mcx(flags, phase)
    qc.h(phase)
    qc.x(phase)
    for flag in flags:
        qc.x(flag)

    for flag, (u, v) in reversed(list(zip(flags, edges))):
        toggle_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
