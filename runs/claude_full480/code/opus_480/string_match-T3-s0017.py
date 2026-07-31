from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "?111"
    n = 8
    m = 4
    offsets = list(range(0, n - m + 1))  # 0..4

    # required '1' positions and '0' positions for pattern at each offset
    def constraints(o):
        ones = []
        zeros = []
        for i, ch in enumerate(pattern):
            if ch == '1':
                ones.append(problem_qubits[o + i])
            elif ch == '0':
                zeros.append(problem_qubits[o + i])
        return ones, zeros

    match_ancillas = ancilla_qubits[:len(offsets)]  # one per offset
    or_ancilla = ancilla_qubits[len(offsets)]       # OR accumulator target

    # compute each offset match into its ancilla
    def compute_matches():
        for idx, o in enumerate(offsets):
            ones, zeros = constraints(o)
            for z in zeros:
                qc.x(z)
            ctrls = ones + zeros
            qc.mcx(ctrls, match_ancillas[idx])
            for z in zeros:
                qc.x(z)

    def uncompute_matches():
        for idx, o in reversed(list(enumerate(offsets))):
            ones, zeros = constraints(o)
            for z in zeros:
                qc.x(z)
            ctrls = ones + zeros
            qc.mcx(ctrls, match_ancillas[idx])
            for z in zeros:
                qc.x(z)

    compute_matches()

    # OR of match_ancillas -> or_ancilla via De Morgan:
    # OR = NOT(AND(NOT match_i))
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, or_ancilla)
    qc.x(or_ancilla)  # now or_ancilla = 1 iff any match
    for a in match_ancillas:
        qc.x(a)

    # phase flip when or_ancilla == 1
    qc.z(or_ancilla)

    # uncompute OR (mirror)
    for a in match_ancillas:
        qc.x(a)
    qc.x(or_ancilla)
    qc.mcx(match_ancillas, or_ancilla)
    for a in match_ancillas:
        qc.x(a)

    uncompute_matches()
