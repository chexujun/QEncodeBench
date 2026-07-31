import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0001"
    m = len(pattern)
    n = len(problem_qubits)
    offsets = list(range(0, n - m + 1))  # 0..4

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    match_ancillas = ancilla_qubits[:len(offsets)]
    or_ancilla = ancilla_qubits[len(offsets)]

    def compute_offset(o, target):
        applied_x = []
        controls = []
        for i, bit in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)
                applied_x.append(q)
            controls.append(q)
        qc.mcx(controls, target)
        for q in applied_x:
            qc.x(q)

    # compute each offset match indicator
    for idx, o in enumerate(offsets):
        compute_offset(o, match_ancillas[idx])

    # OR of match indicators into or_ancilla:
    # or = NOT(AND(NOT m_j)) ; flip all matches, AND->NOT gives OR
    for q in match_ancillas:
        qc.x(q)
    qc.mcx(match_ancillas, or_ancilla)
    for q in match_ancillas:
        qc.x(q)
    qc.x(or_ancilla)  # or_ancilla = OR of matches

    # phase
    qc.z(or_ancilla)

    # uncompute OR
    qc.x(or_ancilla)
    for q in match_ancillas:
        qc.x(q)
    qc.mcx(match_ancillas, or_ancilla)
    for q in match_ancillas:
        qc.x(q)

    # uncompute each offset match indicator (mirror)
    for idx, o in enumerate(reversed(offsets)):
        oo = offsets[len(offsets) - 1 - idx]
        compute_offset(oo, match_ancillas[len(offsets) - 1 - idx])
