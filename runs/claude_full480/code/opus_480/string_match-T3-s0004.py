from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "00?1"
    L = len(pattern)
    n = len(problem_qubits)
    offsets = list(range(0, n - L + 1))

    # constraints[o] = list of (text_index, required_bit) for offset o
    match_ancillas = ancilla_qubits[:len(offsets)]
    phase_ancilla = ancilla_qubits[len(offsets)]

    def constraints_for(o):
        cons = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            cons.append((o + i, int(ch)))
        return cons

    # Compute each offset-match into its ancilla via a multi-controlled X.
    # We flip control polarity with X gates for required_bit == 0.
    def compute_match(o, anc):
        cons = constraints_for(o)
        ctrls = []
        for (idx, bit) in cons:
            q = problem_qubits[idx]
            if bit == 0:
                qc.x(q)
            ctrls.append(q)
        if len(ctrls) == 0:
            qc.x(anc)
        elif len(ctrls) == 1:
            qc.cx(ctrls[0], anc)
        else:
            qc.mcx(ctrls, anc)
        # undo polarity flips (mirror) — keep problem qubits clean
        for (idx, bit) in cons:
            if bit == 0:
                qc.x(problem_qubits[idx])

    # Compute all offset matches
    for o, anc in zip(offsets, match_ancillas):
        compute_match(o, anc)

    # OR of match_ancillas -> phase_ancilla.
    # OR(a_j) == NOT(AND(NOT a_j)). Flip all, AND into phase, flip back.
    for anc in match_ancillas:
        qc.x(anc)
    qc.mcx(list(match_ancillas), phase_ancilla)
    qc.x(phase_ancilla)  # phase_ancilla now = OR of matches
    for anc in match_ancillas:
        qc.x(anc)

    # Apply phase: -1 iff phase_ancilla == 1
    qc.z(phase_ancilla)

    # Uncompute OR
    for anc in match_ancillas:
        qc.x(anc)
    qc.x(phase_ancilla)
    qc.mcx(list(match_ancillas), phase_ancilla)
    for anc in match_ancillas:
        qc.x(anc)

    # Uncompute all offset matches (mirror order)
    for o, anc in zip(reversed(offsets), reversed(match_ancillas)):
        compute_match(o, anc)
