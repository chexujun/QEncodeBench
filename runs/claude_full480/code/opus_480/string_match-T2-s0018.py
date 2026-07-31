from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1101"
    n_text = 5
    offsets = [0, 1]

    match_ancillas = ancilla_qubits[:len(offsets)]
    phase_ancilla = ancilla_qubits[len(offsets)]

    def compute_offset_match(offset, anc):
        # For each fixed (non-wildcard) pattern position, x bit s_(offset+i)
        # must equal pattern[i]. Flip x qubits where pattern[i]==0 so that a
        # match corresponds to all controls == 1, then MCX onto anc.
        controls = []
        flips = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[offset + i]
            controls.append(q)
            if ch == '0':
                flips.append(q)
        for q in flips:
            qc.x(q)
        if controls:
            qc.mcx(controls, anc)
        else:
            qc.x(anc)
        for q in flips:
            qc.x(q)

    # Compute per-offset match flags.
    for k, o in enumerate(offsets):
        compute_offset_match(o, match_ancillas[k])

    # OR of the match flags into phase_ancilla:
    # phase_ancilla = OR(m0, m1) = NOT(AND(NOT m0, NOT m1))
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, phase_ancilla)
    qc.x(phase_ancilla)
    for a in match_ancillas:
        qc.x(a)

    # Apply phase -1 iff phase_ancilla == 1.
    qc.z(phase_ancilla)

    # Uncompute OR.
    for a in match_ancillas:
        qc.x(a)
    qc.x(phase_ancilla)
    qc.mcx(match_ancillas, phase_ancilla)
    for a in match_ancillas:
        qc.x(a)

    # Uncompute per-offset match flags (mirror).
    for k, o in enumerate(offsets):
        compute_offset_match(o, match_ancillas[k])
