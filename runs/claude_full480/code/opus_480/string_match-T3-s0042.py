from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Problem: text length 8 (bits s_0..s_7 on problem_qubits[0..7]).
    # Pattern = "0?00", length 4, offsets o in 0..4.
    # At offset o, match requires: s_(o+0)=0, s_(o+2)=0, s_(o+3)=0 (pos1 is '?').
    # f(x)=1 iff any offset matches (OR over offsets).
    pattern = ['0', '?', '0', '0']
    n_offsets = 5  # o = 0..4

    # Ancillas: use one per offset to hold "match at offset o", then OR them.
    # We have 6 ancillas; 5 for per-offset flags + 1 for the OR/phase target.
    offset_anc = ancilla_qubits[0:n_offsets]   # 5 ancillas
    or_anc = ancilla_qubits[n_offsets]         # 1 ancilla

    def constraints_for_offset(o):
        # list of problem qubit indices that must equal 0 for a match
        idxs = []
        for i, c in enumerate(pattern):
            if c == '?':
                continue
            pos = o + i
            # c is '0' for all fixed positions in "0?00"
            idxs.append(problem_qubits[pos])
        return idxs

    # Compute each offset flag: flag=1 iff all required positions are 0.
    # Flip required qubits so "0" becomes "1", MCX onto flag, flip back.
    def compute_offset_flag(o, flag):
        qs = constraints_for_offset(o)
        for q in qs:
            qc.x(q)
        qc.mcx(qs, flag)
        for q in qs:
            qc.x(q)

    # Compute all offset flags.
    for k in range(n_offsets):
        compute_offset_flag(k, offset_anc[k])

    # OR of the flags into or_anc:
    # or_anc = 1 iff at least one flag is 1.
    # Use: flip all flags, MCX (AND of flipped = NOR) onto or_anc, then X or_anc,
    # then flip flags back. This gives or_anc = OR(flags).
    for k in range(n_offsets):
        qc.x(offset_anc[k])
    qc.mcx(offset_anc, or_anc)
    for k in range(n_offsets):
        qc.x(offset_anc[k])
    qc.x(or_anc)

    # Phase: -1 iff or_anc == 1.
    qc.z(or_anc)

    # Uncompute OR.
    qc.x(or_anc)
    for k in range(n_offsets):
        qc.x(offset_anc[k])
    qc.mcx(offset_anc, or_anc)
    for k in range(n_offsets):
        qc.x(offset_anc[k])

    # Uncompute offset flags (mirror).
    for k in reversed(range(n_offsets)):
        compute_offset_flag(k, offset_anc[k])
