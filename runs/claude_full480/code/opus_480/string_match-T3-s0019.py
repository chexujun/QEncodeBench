from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "101?"
    n = 8
    m = len(pattern)
    offsets = list(range(n - m + 1))  # 0..4

    # Fixed pattern positions (non-wildcard) for each offset
    match_anc = ancilla_qubits[:len(offsets)]   # one ancilla per offset (5)
    or_anc = ancilla_qubits[len(offsets)]       # accumulator ancilla (1)

    def compute_offset(o, target):
        # Determine required literals: for each pattern char that isn't '?',
        # text bit s_(o+i) must equal int(pattern[i]).
        controls = []
        flipped = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            controls.append(q)
            if ch == '0':
                # want bit == 0 -> flip so control is active when bit is 0
                qc.x(q)
                flipped.append(q)
        # AND of all controls into target
        qc.mcx(controls, target)
        # undo flips
        for q in flipped:
            qc.x(q)

    # Compute each offset match indicator
    for idx, o in enumerate(offsets):
        compute_offset(o, match_anc[idx])

    # OR of all match indicators into or_anc:
    # or_anc = 1 if any match_anc == 1.
    # Use De Morgan: NOT(all zero). Flip all match_anc, mcx into or_anc, flip back,
    # then X or_anc.
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)
    qc.x(or_anc)

    # Phase
    qc.z(or_anc)

    # Uncompute OR
    qc.x(or_anc)
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)

    # Uncompute each offset match indicator (mirror)
    for idx, o in enumerate(reversed(offsets)):
        real_o = offsets[len(offsets) - 1 - idx]
        compute_offset(real_o, match_anc[len(offsets) - 1 - idx])
