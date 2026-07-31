from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0100"
    m = len(pattern)
    n = len(problem_qubits)
    offsets = list(range(0, n - m + 1))  # 0..4

    # For each offset, we need an ancilla that is 1 iff the pattern matches at that offset.
    # match at offset o: for each pattern position i with pattern[i] in {0,1},
    #   s_(o+i) == int(pattern[i]).
    # We compute per-offset match into a dedicated ancilla via MCX with appropriate
    # controls (X-conjugated for pattern bit 0). Then OR the offset-match ancillas
    # to get f, apply phase, and uncompute everything.

    match_ancillas = ancilla_qubits[:len(offsets)]  # 5 ancillas for 5 offsets
    or_ancilla = ancilla_qubits[len(offsets)]        # 1 ancilla for the OR result

    # Positions (fixed, i.e. pattern[i] != '?') for each offset -> list of (qubit, want_bit)
    def constraints(o):
        cons = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            cons.append((problem_qubits[o + i], int(ch)))
        return cons

    # ---- compute per-offset match ancillas ----
    for idx, o in enumerate(offsets):
        cons = constraints(o)
        anc = match_ancillas[idx]
        ctrls = [q for (q, _) in cons]
        # X-flip controls whose desired bit is 0, so control-on-1 tests equality
        zeros = [q for (q, w) in cons if w == 0]
        for q in zeros:
            qc.x(q)
        qc.mcx(ctrls, anc)
        for q in zeros:
            qc.x(q)

    # ---- OR of match ancillas into or_ancilla ----
    # OR(a_0..a_k) = NOT(AND(NOT a_i)).  Compute via: flip all, mcx into or, flip back,
    # then X the or_ancilla.
    for anc in match_ancillas:
        qc.x(anc)
    qc.mcx(match_ancillas, or_ancilla)
    for anc in match_ancillas:
        qc.x(anc)
    qc.x(or_ancilla)  # or_ancilla now = OR of matches = f(x)

    # ---- phase ----
    qc.z(or_ancilla)

    # ---- uncompute OR ----
    qc.x(or_ancilla)
    for anc in match_ancillas:
        qc.x(anc)
    qc.mcx(match_ancillas, or_ancilla)
    for anc in match_ancillas:
        qc.x(anc)

    # ---- uncompute per-offset match ancillas (mirror) ----
    for idx, o in reversed(list(enumerate(offsets))):
        cons = constraints(o)
        anc = match_ancillas[idx]
        ctrls = [q for (q, _) in cons]
        zeros = [q for (q, w) in cons if w == 0]
        for q in zeros:
            qc.x(q)
        qc.mcx(ctrls, anc)
        for q in zeros:
            qc.x(q)
