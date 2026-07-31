from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0010"
    n = 8
    m = len(pattern)
    offsets = list(range(n - m + 1))  # 0..4

    # Precompute, for each offset, the list of (text_index, required_bit)
    # for non-wildcard pattern positions.
    constraints = []
    for o in offsets:
        cons = []
        for i, c in enumerate(pattern):
            if c == '?':
                continue
            cons.append((o + i, int(c)))
        constraints.append(cons)

    match_anc = ancilla_qubits[:len(offsets)]   # one ancilla per offset (5)
    or_anc = ancilla_qubits[len(offsets)]        # OR-accumulator ancilla (1)

    def compute_match(o_idx):
        cons = constraints[o_idx]
        a = match_anc[o_idx]
        ctrls = []
        for (ti, bit) in cons:
            q = problem_qubits[ti]
            if bit == 0:
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, a)
        # a == 1 iff all constrained bits equal required values
        for (ti, bit) in cons:
            q = problem_qubits[ti]
            if bit == 0:
                qc.x(q)

    def uncompute_match(o_idx):
        compute_match(o_idx)  # self-inverse structure

    # Compute all per-offset match flags.
    for o_idx in range(len(offsets)):
        compute_match(o_idx)

    # OR of all match flags into or_anc:
    # or_anc = 1 iff at least one match flag is 1.
    # Use De Morgan: flip all flags, MCX gives AND(flipped)=NOR, X the result.
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)   # or_anc = 1 iff all flags were 0 (after flip -> all flipped ==1)
    qc.x(or_anc)                # now or_anc = 1 iff at least one flag == 1
    for a in match_anc:
        qc.x(a)

    # Phase.
    qc.z(or_anc)

    # Uncompute OR.
    for a in match_anc:
        qc.x(a)
    qc.x(or_anc)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)

    # Uncompute match flags.
    for o_idx in reversed(range(len(offsets))):
        uncompute_match(o_idx)
