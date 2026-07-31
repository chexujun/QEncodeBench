```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4)]

    # XOR-of-products representation of decoded-color equality for an edge.
    # Entries correspond to [u_low, u_high, v_low, v_high];
    # -1 denotes a don't-care control.
    equality_terms = [
        (-1, -1, 0, 0),
        (-1, 0, 1, 1),
        (0, 1, 0, -1),
        (1, -1, 1, 1),
        (1, 0, -1, 0),
    ]

    def apply_term(qubits, pattern, target):
        for qubit, bit in zip(qubits, pattern):
            if bit == 0:
                qc.x(qubit)

        controls = [qubit for qubit, bit in zip(qubits, pattern) if bit != -1]
        qc.mcx(controls, target)

        for qubit, bit in reversed(list(zip(qubits, pattern))):
            if bit == 0:
                qc.x(qubit)

    # Compute one equality flag per edge.  A zero flag means the colors differ.
    for (u, v), flag in zip(edges, ancilla_qubits[:7]):
        edge_qubits = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]
        for term in equality_terms:
            apply_term(edge_qubits, term, flag)

    # Phase-kickback: mark precisely when no edge has equal decoded colors.
    phase_qubit = ancilla_qubits[7]
    qc.x(phase_qubit)
    qc.h(phase_qubit)
    qc.mcx(ancilla_qubits[:7], phase_qubit, ctrl_state="0" * 7)
    qc.h(phase_qubit)
    qc.x(phase_qubit)

    # Uncompute all edge flags.
    for (u, v), flag in reversed(list(zip(edges, ancilla_qubits[:7]))):
        edge_qubits = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]
        for term in reversed(equality_terms):
            apply_term(edge_qubits, term, flag)
```
