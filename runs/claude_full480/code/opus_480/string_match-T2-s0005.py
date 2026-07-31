from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1011"
    n_text = 6
    p = len(pattern)
    offsets = list(range(0, n_text - p + 1))  # 0,1,2

    # For each offset, the match-predicate is an AND over non-wildcard positions.
    # match_o = AND_i ( s_(o+i) == pattern[i] ).
    # f = OR_o match_o.
    # Use one ancilla per offset to hold match_o, then OR via
    # De Morgan on the phase, or directly build a multi-target scheme.
    #
    # We compute each match_o into a dedicated ancilla (there are 3 offsets,
    # ancilla_qubits[0..2]), then apply an overall phase for OR using the
    # standard "phase if any ancilla set" via De Morgan:
    #   OR = NOT(AND(NOT a_o)).
    # We implement OR-phase by: flip all match ancillas (a->NOT a), then a
    # multi-controlled Z conditioned on all being 1 (i.e. all original 0 =>
    # no match => f=0 gets phase), which is the complement. To get phase on
    # f=1 states we instead phase when NOT(all no-match): apply global-style
    # trick: phase everything then subtract the no-match phase. Simpler and
    # exact: mark f=0 with -1 and add an overall -1 => equivalent up to
    # global phase to marking f=1. Global phase is accepted.

    match_anc = ancilla_qubits[:len(offsets)]

    def compute_match(o, target):
        # Set text qubits so that a match => all controls are 1, using X to
        # account for pattern bits equal to 0. Wildcards are skipped.
        ctrls = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            if ch == '0':
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, target)
        # undo the X flips
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            if ch == '0':
                qc.x(problem_qubits[o + i])

    # compute all match ancillas
    for o, a in zip(offsets, match_anc):
        compute_match(o, a)

    # Now match_anc holds the per-offset match bits. We want phase -1 on any
    # state with at least one match bit set (f=1).
    # Use De Morgan: phase on f=0 (all match bits 0) and accept global phase.
    #   Flip all match bits, multi-controlled-Z on all => phases the all-zero
    #   (original) state = the f=0 states. Then add overall -1 via a global
    #   phase so f=1 states carry the -1 (global phase accepted).
    for a in match_anc:
        qc.x(a)
    if len(match_anc) == 1:
        qc.z(match_anc[0])
    else:
        qc.h(match_anc[-1])
        qc.mcx(match_anc[:-1], match_anc[-1])
        qc.h(match_anc[-1])
    for a in match_anc:
        qc.x(a)

    # global phase to convert "phase on f=0" into "phase on f=1" (accepted)
    qc.global_phase += math.pi

    # uncompute all match ancillas (mirror)
    for o, a in reversed(list(zip(offsets, match_anc))):
        compute_match(o, a)
