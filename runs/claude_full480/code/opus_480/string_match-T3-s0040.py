import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1010"
    n = len(problem_qubits)
    m = len(pattern)
    offsets = list(range(n - m + 1))  # 0..4

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    match_anc = ancilla_qubits[:len(offsets)]  # one ancilla per offset
    or_anc = ancilla_qubits[len(offsets)]      # OR-accumulator ancilla

    def compute_offset(o, target):
        controls = []
        for i, bit in fixed:
            q = problem_qubits[o + i]
            if bit == 0:
                qc.x(q)
            controls.append(q)
        qc.mcx(controls, target)
        for i, bit in fixed:
            if bit == 0:
                qc.x(problem_qubits[o + i])

    # compute each offset match indicator
    for idx, o in enumerate(offsets):
        compute_offset(o, match_anc[idx])

    # OR of all match indicators into or_anc:
    # or_anc = 1 iff any match_anc == 1
    # Use: X on all, MCX -> or_anc gives AND(not match)=NOR, then X to get OR
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)
    qc.x(or_anc)

    # phase
    qc.z(or_anc)

    # uncompute OR
    qc.x(or_anc)
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)

    # uncompute each offset match indicator
    for idx, o in enumerate(offsets):
        compute_offset(o, match_anc[idx])
