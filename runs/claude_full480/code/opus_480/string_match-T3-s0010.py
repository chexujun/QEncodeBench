from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1110"
    L = 4
    n = 8
    offsets = list(range(0, n - L + 1))  # 0..4, 5 offsets

    match_ancillas = ancilla_qubits[:len(offsets)]  # one per offset (5)
    or_ancilla = ancilla_qubits[len(offsets)]        # final OR flag

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    def compute_offset(o, tgt):
        ctrls = []
        flips = []
        for (i, bit) in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, tgt)
        for q in flips:
            qc.x(q)

    # compute each offset match into its ancilla
    for idx, o in enumerate(offsets):
        compute_offset(o, match_ancillas[idx])

    # OR of match_ancillas into or_ancilla:
    # or = 1 iff any match ==1. Use De Morgan: flip all matches, mcx (AND of NOTs) -> NOT or, then flip.
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, or_ancilla)
    qc.x(or_ancilla)
    for a in match_ancillas:
        qc.x(a)

    # phase
    qc.z(or_ancilla)

    # uncompute or_ancilla
    for a in match_ancillas:
        qc.x(a)
    qc.x(or_ancilla)
    qc.mcx(match_ancillas, or_ancilla)
    for a in match_ancillas:
        qc.x(a)

    # uncompute each offset match
    for idx, o in enumerate(offsets):
        compute_offset(o, match_ancillas[idx])
