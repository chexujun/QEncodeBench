from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0010?1"
    n = 7
    offsets = [0, 1]

    match_ancillas = []
    for idx, o in enumerate(offsets):
        # qubits that must equal a specified bit for this offset
        controls = []
        flip_zeros = []  # qubits where pattern bit is '0' -> need X so control on 1
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            controls.append(q)
            if ch == '0':
                flip_zeros.append(q)

        # compute AND of (matching) into match ancilla
        ma = ancilla_qubits[idx]
        for q in flip_zeros:
            qc.x(q)
        qc.mcx(controls, ma)
        for q in flip_zeros:
            qc.x(q)
        match_ancillas.append(ma)

    # OR of match_ancillas -> phase -1 iff any match.
    # OR(a,b) via: result = 1 - (1-a)(1-b). Compute NOT-both-zero.
    # Flip each match ancilla, AND into the OR ancilla gives (both zero);
    # then phase when NOT both zero = -Z on that state.
    orc = ancilla_qubits[2]
    for ma in match_ancillas:
        qc.x(ma)
    # orc = 1 iff all match_ancillas were 0 (i.e. no match)
    qc.mcx(match_ancillas, orc)
    for ma in match_ancillas:
        qc.x(ma)

    # We want phase -1 iff at least one match, i.e. iff orc == 0.
    # Apply phase -1 on orc==0: X, Z, X on orc.
    qc.x(orc)
    qc.z(orc)
    qc.x(orc)

    # uncompute orc
    for ma in match_ancillas:
        qc.x(ma)
    qc.mcx(match_ancillas, orc)
    for ma in match_ancillas:
        qc.x(ma)

    # uncompute match ancillas
    for idx, o in enumerate(offsets):
        controls = []
        flip_zeros = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            controls.append(q)
            if ch == '0':
                flip_zeros.append(q)
        ma = ancilla_qubits[idx]
        for q in flip_zeros:
            qc.x(q)
        qc.mcx(controls, ma)
        for q in flip_zeros:
            qc.x(q)
