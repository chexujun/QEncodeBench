from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1101"
    m = len(pattern)
    n = len(problem_qubits)
    offsets = list(range(0, n - m + 1))  # 0..4

    match_flags = ancilla_qubits[:len(offsets)]  # one ancilla per offset (5)
    final = ancilla_qubits[len(offsets)]          # OR-accumulator ancilla (index 5)

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    def compute_offset(o, flag):
        ctrls = []
        for i, bit in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, flag)
        for i, bit in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)

    # Compute all offset match flags
    for o, flag in zip(offsets, match_flags):
        compute_offset(o, flag)

    # OR of all flags into `final`: final = OR(flags)
    # final = 1 iff any flag is 1. Use De Morgan: NOT(all NOT flags).
    for flag in match_flags:
        qc.x(flag)
    qc.mcx(match_flags, final)
    qc.x(final)
    for flag in match_flags:
        qc.x(flag)

    # Phase
    qc.z(final)

    # Uncompute OR
    for flag in match_flags:
        qc.x(flag)
    qc.x(final)
    qc.mcx(match_flags, final)
    for flag in match_flags:
        qc.x(flag)

    # Uncompute offset flags (mirror)
    for o, flag in zip(offsets, match_flags):
        compute_offset(o, flag)
