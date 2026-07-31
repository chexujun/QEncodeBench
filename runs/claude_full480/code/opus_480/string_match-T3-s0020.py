from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0101"
    n_text = 8
    p_len = len(pattern)
    offsets = list(range(n_text - p_len + 1))  # 0..4

    # For each offset, we need an ancilla that becomes |1> iff the pattern
    # matches at that offset. We have len(offsets)=5 match-ancillas plus
    # one final ancilla for the OR result = 6 ancillas total.
    match_anc = ancilla_qubits[:len(offsets)]   # 5 ancillas
    or_anc = ancilla_qubits[len(offsets)]        # 1 ancilla

    # positions in the pattern that are constrained (not '?')
    def constrained(o):
        return [(i, pattern[i]) for i in range(p_len) if pattern[i] != '?']

    def compute_matches():
        for idx, o in enumerate(offsets):
            cons = constrained(o)
            ctrl_qubits = []
            flip = []
            for (i, ch) in cons:
                q = problem_qubits[o + i]
                if ch == '0':
                    qc.x(q)
                    flip.append(q)
                ctrl_qubits.append(q)
            # match_anc[idx] = AND of all (s == required)
            qc.mcx(ctrl_qubits, match_anc[idx])
            # undo the X flips
            for q in flip:
                qc.x(q)

    # Compute all match ancillas
    compute_matches()

    # OR of match ancillas into or_anc:
    # or_anc = 1 iff any match_anc == 1.
    # Use: or = NOT(AND of NOT match_i). Flip all match_anc, mcx into or, unflip,
    # then X on or_anc.
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)
    qc.x(or_anc)

    # Apply phase: -1 iff or_anc == 1
    qc.z(or_anc)

    # Uncompute or_anc (mirror)
    qc.x(or_anc)
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)

    # Uncompute match ancillas (mirror of compute_matches)
    for idx, o in enumerate(offsets):
        cons = constrained(o)
        ctrl_qubits = []
        flip = []
        for (i, ch) in cons:
            q = problem_qubits[o + i]
            if ch == '0':
                qc.x(q)
                flip.append(q)
            ctrl_qubits.append(q)
        qc.mcx(ctrl_qubits, match_anc[idx])
        for q in flip:
            qc.x(q)
