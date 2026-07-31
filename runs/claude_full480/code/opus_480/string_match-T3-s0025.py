from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0110"
    m = len(pattern)
    n = len(problem_qubits)
    offsets = list(range(0, n - m + 1))  # 0..4

    # For each offset, an ancilla holds whether the pattern matches at that offset.
    match_ancillas = ancilla_qubits[:len(offsets)]
    # One extra ancilla to collect the OR / hold the phase target.
    final_anc = ancilla_qubits[len(offsets)]

    def compute_offset_match(o, target):
        # target = AND over pattern positions of (s_(o+i) == pattern[i])
        # For pattern char '1': need qubit == 1 (use as-is control).
        # For pattern char '0': need qubit == 0 (X-conjugate the control).
        # '?' : skip.
        controls = []
        flips = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            controls.append(q)
            if ch == '0':
                flips.append(q)
        # Flip zeros so that "match" == all controls are 1.
        for q in flips:
            qc.x(q)
        if controls:
            qc.mcx(controls, target)
        else:
            qc.x(target)
        # Restore
        for q in flips:
            qc.x(q)

    # Compute each offset match into its ancilla.
    for idx, o in enumerate(offsets):
        compute_offset_match(o, match_ancillas[idx])

    # OR of all match ancillas into final_anc:
    # final = OR(m_j) = NOT(AND(NOT m_j)).
    # Flip all match ancillas, do mcx of their complements -> final gets AND of complements,
    # then X final to get the OR. Then unflip match ancillas.
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final_anc)
    for a in match_ancillas:
        qc.x(a)
    qc.x(final_anc)  # final_anc = OR

    # Phase kick.
    qc.z(final_anc)

    # Uncompute final_anc (mirror of the OR computation).
    qc.x(final_anc)
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final_anc)
    for a in match_ancillas:
        qc.x(a)

    # Uncompute each offset match (mirror).
    for idx, o in reversed(list(enumerate(offsets))):
        compute_offset_match(o, match_ancillas[idx])
