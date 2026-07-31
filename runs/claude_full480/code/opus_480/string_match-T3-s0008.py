from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "11?0"
    n = 8
    L = len(pattern)
    offsets = list(range(n - L + 1))  # 0..4

    # ancilla layout: one ancilla per offset holds "match at this offset",
    # then one final ancilla accumulates the OR for the phase.
    off_anc = ancilla_qubits[:len(offsets)]     # 5 ancillas
    or_anc = ancilla_qubits[len(offsets)]       # 1 ancilla

    def fixed_positions(o):
        ctrls = []
        neg = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            ctrls.append(q)
            neg.append(ch == '0')
        return ctrls, neg

    def compute_offset(o, target):
        ctrls, neg = fixed_positions(o)
        for q, isneg in zip(ctrls, neg):
            if isneg:
                qc.x(q)
        qc.mcx(ctrls, target)
        for q, isneg in zip(ctrls, neg):
            if isneg:
                qc.x(q)

    # Compute per-offset match flags
    for o, target in zip(offsets, off_anc):
        compute_offset(o, target)

    # OR of all offset flags into or_anc:
    # OR = NOT(AND(NOT flags)). Flip all flags, MCX (all zero originally ->
    # all one after flip means no match), then flip or_anc semantics.
    for a in off_anc:
        qc.x(a)
    qc.mcx(off_anc, or_anc)   # or_anc = 1 iff all flags were 0 (no match)
    qc.x(or_anc)              # or_anc = 1 iff at least one match
    for a in off_anc:
        qc.x(a)

    # Phase
    qc.z(or_anc)

    # Uncompute OR
    for a in off_anc:
        qc.x(a)
    qc.x(or_anc)
    qc.mcx(off_anc, or_anc)
    for a in off_anc:
        qc.x(a)

    # Uncompute per-offset flags (mirror)
    for o, target in zip(offsets, off_anc):
        compute_offset(o, target)
