import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "01110"
    m = len(pattern)
    n = len(problem_qubits)
    offsets = [0, 1, 2]

    match_ancillas = ancilla_qubits[:len(offsets)]
    final_ancilla = ancilla_qubits[len(offsets)]

    def compute_match(o, target):
        fixed = []
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[o + i]
            fixed.append((q, pc))
        flipped = []
        for q, pc in fixed:
            if pc == '0':
                qc.x(q)
                flipped.append(q)
        ctrls = [q for q, pc in fixed]
        qc.mcx(ctrls, target)
        for q in flipped:
            qc.x(q)

    for idx, o in enumerate(offsets):
        compute_match(o, match_ancillas[idx])

    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final_ancilla)
    for a in match_ancillas:
        qc.x(a)
    qc.x(final_ancilla)

    qc.z(final_ancilla)

    qc.x(final_ancilla)
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final_ancilla)
    for a in match_ancillas:
        qc.x(a)

    for idx, o in enumerate(reversed(offsets)):
        ridx = len(offsets) - 1 - idx
        compute_match(o, match_ancillas[ridx])
