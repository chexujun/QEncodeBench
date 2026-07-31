from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    pattern = "111?"
    n = len(problem_qubits)
    m = len(pattern)
    offsets = list(range(0, n - m + 1))  # 0..4

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    match_anc = ancilla_qubits[:len(offsets)]   # one ancilla per offset
    or_anc = ancilla_qubits[len(offsets)]       # OR-accumulator ancilla

    def compute_matches():
        for k, o in enumerate(offsets):
            a = match_anc[k]
            ctrls = []
            xed = []
            for (i, bit) in fixed:
                q = problem_qubits[o + i]
                if bit == 0:
                    qc.x(q)
                    xed.append(q)
                ctrls.append(q)
            qc.mcx(ctrls, a)
            for q in xed:
                qc.x(q)

    def uncompute_matches():
        for k in reversed(range(len(offsets))):
            o = offsets[k]
            a = match_anc[k]
            ctrls = []
            xed = []
            for (i, bit) in fixed:
                q = problem_qubits[o + i]
                if bit == 0:
                    qc.x(q)
                    xed.append(q)
                ctrls.append(q)
            qc.mcx(ctrls, a)
            for q in xed:
                qc.x(q)

    # OR of the match ancillas into or_anc:
    # or = NOT(AND of NOT(match_k))  -> flip all matches, AND into or, then
    # phase, then undo.
    compute_matches()

    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)
    qc.x(or_anc)  # or_anc = OR of matches

    qc.z(or_anc)

    qc.x(or_anc)
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)

    uncompute_matches()
