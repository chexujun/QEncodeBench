from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "111"
    n = len(problem_qubits)
    m = len(pattern)
    offsets = list(range(n - m + 1))  # 0..5

    # required positions per offset: pattern has no wildcards here
    match_flags = ancilla_qubits[:len(offsets)]  # 6 ancillas, one per offset
    final = ancilla_qubits[len(offsets)]          # 1 ancilla for OR result

    # compute: match_flag[o] = AND over required text bits
    for idx, o in enumerate(offsets):
        controls = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            if ch == '0':
                qc.x(q)  # so that control on |1> means bit==0
            controls.append(q)
        qc.mcx(controls, match_flags[idx])
        # undo the x's used to test 0-bits
        for i, ch in enumerate(pattern):
            if ch == '0':
                qc.x(problem_qubits[o + i])

    # OR of all match_flags into `final`:
    # final = 1 iff any match_flag == 1.  Use: final := NOT(AND of NOT flags)
    for mf in match_flags:
        qc.x(mf)
    qc.x(final)
    qc.mcx(match_flags, final)  # final = 1 XOR (all flags were 1-after-not)
    # now final = 1 iff at least one original flag == 1
    for mf in match_flags:
        qc.x(mf)

    # phase
    qc.z(final)

    # uncompute final
    for mf in match_flags:
        qc.x(mf)
    qc.mcx(match_flags, final)
    qc.x(final)
    for mf in match_flags:
        qc.x(mf)

    # uncompute match_flags (mirror)
    for idx, o in enumerate(offsets):
        controls = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            if ch == '0':
                qc.x(q)
            controls.append(q)
        qc.mcx(controls, match_flags[idx])
        for i, ch in enumerate(pattern):
            if ch == '0':
                qc.x(problem_qubits[o + i])
