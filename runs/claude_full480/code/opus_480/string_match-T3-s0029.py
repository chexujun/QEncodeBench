from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1?00"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    match_ancillas = ancilla_qubits[:5]
    final = ancilla_qubits[5]

    def compute_offset_match(o, tgt):
        used = []
        for (i, bit) in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)
            used.append(q)
        qc.mcx(used, tgt)
        for (i, bit) in fixed:
            if bit == 0:
                qc.x(problem_qubits[o + i])

    for o in range(5):
        compute_offset_match(o, match_ancillas[o])

    qc.x(match_ancillas)
    qc.mcx(list(match_ancillas), final)
    qc.x(match_ancillas)
    qc.x(final)

    qc.z(final)

    qc.x(final)
    qc.x(match_ancillas)
    qc.mcx(list(match_ancillas), final)
    qc.x(match_ancillas)

    for o in reversed(range(5)):
        compute_offset_match(o, match_ancillas[o])
