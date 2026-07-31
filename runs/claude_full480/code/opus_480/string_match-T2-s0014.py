import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "101"
    n = len(problem_qubits)
    m = len(pattern)
    offsets = list(range(0, n - m + 1))  # 0,1,2

    match_flags = ancilla_qubits[:len(offsets)]  # one flag per offset
    final = ancilla_qubits[len(offsets)]          # OR-result ancilla

    def compute_offset(o, flag):
        fixed = [(problem_qubits[o + i], pattern[i]) for i in range(m)
                 if pattern[i] != '?']
        # For a match: every fixed position must equal its pattern bit.
        # Flip qubits whose required value is '0', so match <=> all controls are 1.
        for q, c in fixed:
            if c == '0':
                qc.x(q)
        ctrls = [q for q, _ in fixed]
        if ctrls:
            qc.mcx(ctrls, flag)
        else:
            qc.x(flag)
        for q, c in fixed:
            if c == '0':
                qc.x(q)

    # Compute per-offset match flags
    for o, flag in zip(offsets, match_flags):
        compute_offset(o, flag)

    # OR of the flags into `final`: final = 1 iff any flag == 1.
    # NOT(all flags == 0). Flip flags, mcx (final=1 iff all flipped==1 => all flags 0),
    # then X on final to invert, then unflip.
    for flag in match_flags:
        qc.x(flag)
    qc.mcx(match_flags, final)
    qc.x(final)
    for flag in match_flags:
        qc.x(flag)

    # Phase
    qc.z(final)

    # Uncompute OR (mirror)
    for flag in match_flags:
        qc.x(flag)
    qc.x(final)
    qc.mcx(match_flags, final)
    for flag in match_flags:
        qc.x(flag)

    # Uncompute per-offset flags (mirror)
    for o, flag in zip(offsets, match_flags):
        compute_offset(o, flag)
