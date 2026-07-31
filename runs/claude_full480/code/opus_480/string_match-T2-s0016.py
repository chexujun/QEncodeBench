from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1?010"
    n_off = 3  # offsets 0..2
    match_anc = ancilla_qubits[0:n_off]   # one flag per offset
    final_anc = ancilla_qubits[n_off]      # OR-of-offsets flag

    def match_flag(offset, anc):
        # positions to constrain: pattern chars that are not '?'
        fixed = [(i, c) for i, c in enumerate(pattern) if c != '?']
        # need anc = AND over fixed positions of (s_{offset+i} == c)
        # For c=='0', we want the qubit to be 0 -> flip it so control on 1 means matched.
        ctrls = []
        flips = []
        for i, c in fixed:
            q = problem_qubits[offset + i]
            if c == '0':
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, anc)
        for q in flips:
            qc.x(q)

    # compute per-offset match flags
    for o in range(n_off):
        match_flag(o, match_anc[o])

    # final = OR(match flags). Compute via De Morgan:
    # final = 1 unless all match flags are 0.
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, final_anc)
    qc.x(final_anc)
    for a in match_anc:
        qc.x(a)

    # phase
    qc.z(final_anc)

    # uncompute final flag (mirror)
    for a in match_anc:
        qc.x(a)
    qc.x(final_anc)
    qc.mcx(match_anc, final_anc)
    for a in match_anc:
        qc.x(a)

    # uncompute per-offset match flags (mirror, reverse order)
    for o in reversed(range(n_off)):
        match_flag(o, match_anc[o])
