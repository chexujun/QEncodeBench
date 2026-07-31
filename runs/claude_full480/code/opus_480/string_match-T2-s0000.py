from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0011?"
    n = 6
    L = 5
    offsets = [0, 1]

    match_ancillas = ancilla_qubits[:len(offsets)]
    phase_ancilla = ancilla_qubits[len(offsets)]

    def compute_match(offset, target_anc):
        # collect fixed positions: (qubit, required_bit)
        fixed = []
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[offset + i]
            fixed.append((q, int(pc)))
        # flip qubits whose required bit is 0 so that AND over all == 1 means match
        flipped = []
        for q, b in fixed:
            if b == 0:
                qc.x(q)
                flipped.append(q)
        ctrls = [q for q, _ in fixed]
        qc.mcx(ctrls, target_anc)
        # unflip
        for q in flipped:
            qc.x(q)

    def uncompute_match(offset, target_anc):
        fixed = []
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[offset + i]
            fixed.append((q, int(pc)))
        flipped = []
        for q, b in fixed:
            if b == 0:
                qc.x(q)
                flipped.append(q)
        ctrls = [q for q, _ in fixed]
        qc.mcx(ctrls, target_anc)
        for q in flipped:
            qc.x(q)

    # compute each offset match flag
    for k, offset in enumerate(offsets):
        compute_match(offset, match_ancillas[k])

    # phase_ancilla should be 1 iff ANY match flag is 1 (OR).
    # OR via De Morgan: flip all flags, AND (mcx) into phase_ancilla, then the
    # phase_ancilla holds NOT(OR) initially; we build OR into phase_ancilla.
    # Use: phase = NOT( AND(NOT flags) ). Set phase_ancilla = 1, then subtract.
    # Simpler: initialize phase_ancilla via X, then mcx of NOT-flags flips it to 0 when none match.
    qc.x(phase_ancilla)
    for k in range(len(offsets)):
        qc.x(match_ancillas[k])
    qc.mcx(match_ancillas, phase_ancilla)
    for k in range(len(offsets)):
        qc.x(match_ancillas[k])
    # now phase_ancilla == OR(flags)

    # apply phase
    qc.z(phase_ancilla)

    # uncompute phase_ancilla
    for k in range(len(offsets)):
        qc.x(match_ancillas[k])
    qc.mcx(match_ancillas, phase_ancilla)
    for k in range(len(offsets)):
        qc.x(match_ancillas[k])
    qc.x(phase_ancilla)

    # uncompute match flags
    for k, offset in enumerate(offsets):
        uncompute_match(offset, match_ancillas[k])
