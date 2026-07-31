from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1111"
    n = 8
    L = len(pattern)
    num_offsets = n - L + 1  # 5

    match_ancillas = ancilla_qubits[:num_offsets]  # one per offset
    or_ancilla = ancilla_qubits[num_offsets]       # OR-accumulator

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    def compute_match(o, tgt):
        controls = []
        for (i, bit) in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)
            controls.append(q)
        if controls:
            qc.mcx(controls, tgt)
        else:
            qc.x(tgt)
        for (i, bit) in fixed:
            if bit == 0:
                qc.x(problem_qubits[o + i])

    # compute each offset match flag
    for idx, o in enumerate(range(num_offsets)):
        compute_match(o, match_ancillas[idx])

    # OR of all match flags into or_ancilla:
    # or = 1 - prod(1 - m_k). Compute NOT-any via flipping.
    # Use: set or_ancilla to OR via inclusion using X + mcx on negated flags.
    # Flip all flags, mcx(all flags -> or) gives AND of NOTs = NOR, then X.
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, or_ancilla)  # or_ancilla = AND(not m_k) = NOR
    for a in match_ancillas:
        qc.x(a)
    qc.x(or_ancilla)  # or_ancilla = OR(m_k)

    # phase
    qc.z(or_ancilla)

    # uncompute OR
    qc.x(or_ancilla)
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, or_ancilla)
    for a in match_ancillas:
        qc.x(a)

    # uncompute match flags (mirror)
    for idx, o in reversed(list(enumerate(range(num_offsets)))):
        compute_match(o, match_ancillas[idx])
