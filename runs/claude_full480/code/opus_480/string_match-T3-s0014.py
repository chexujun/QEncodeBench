from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0111"
    L = 8
    m = len(pattern)
    offsets = list(range(0, L - m + 1))  # 0..4

    # match-flag ancillas: one per offset
    match_flags = ancilla_qubits[:len(offsets)]      # 5 ancillas
    or_flag = ancilla_qubits[len(offsets)]           # 1 ancilla for OR result

    # positions that are NOT wildcards, with their required value
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    def compute_matches():
        for k, o in enumerate(offsets):
            ctrls = []
            xed = []
            for (i, val) in fixed:
                q = problem_qubits[o + i]
                if val == 0:
                    qc.x(q)
                    xed.append(q)
                ctrls.append(q)
            qc.mcx(ctrls, match_flags[k])
            for q in xed:
                qc.x(q)

    def uncompute_matches():
        for k, o in enumerate(offsets):
            ctrls = []
            xed = []
            for (i, val) in fixed:
                q = problem_qubits[o + i]
                if val == 0:
                    qc.x(q)
                    xed.append(q)
                ctrls.append(q)
            qc.mcx(ctrls, match_flags[k])
            for q in xed:
                qc.x(q)

    # Compute per-offset match flags
    compute_matches()

    # OR of match_flags into or_flag:
    # or_flag = 1 iff at least one match_flag == 1
    # Use De Morgan: flip all flags, MCX (all zero => target stays 0), then
    # or_flag holds AND-of-negations; invert meaning via X on target.
    for q in match_flags:
        qc.x(q)
    qc.mcx(match_flags, or_flag)   # or_flag = AND(not flag_k) = NOR
    qc.x(or_flag)                  # or_flag = OR(flag_k)
    for q in match_flags:
        qc.x(q)

    # Phase kick
    qc.z(or_flag)

    # Uncompute OR
    for q in match_flags:
        qc.x(q)
    qc.x(or_flag)
    qc.mcx(match_flags, or_flag)
    for q in match_flags:
        qc.x(q)

    # Uncompute per-offset match flags
    uncompute_matches()
