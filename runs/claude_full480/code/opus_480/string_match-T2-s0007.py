from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # text length 6, pattern "?1111" length 5, offsets o in {0, 1}.
    # Pattern position i compared to s_(o+i). '?' at position 0 matches anything.
    # So for offset o, match iff s_(o+1), s_(o+2), s_(o+3), s_(o+4) are all 1.
    # offset 0: s1 & s2 & s3 & s4
    # offset 1: s2 & s3 & s4 & s5
    a0 = ancilla_qubits[0]  # holds match-at-offset-0
    a1 = ancilla_qubits[1]  # holds match-at-offset-1
    flag = ancilla_qubits[2]  # holds OR of the two

    s = problem_qubits

    # compute a0 = s1 & s2 & s3 & s4
    qc.mcx([s[1], s[2], s[3], s[4]], a0)
    # compute a1 = s2 & s3 & s4 & s5
    qc.mcx([s[2], s[3], s[4], s[5]], a1)

    # flag = a0 OR a1 = NOT( (NOT a0) AND (NOT a1) )
    qc.x(a0)
    qc.x(a1)
    qc.x(flag)
    qc.ccx(a0, a1, flag)
    # now flag = 1 iff (a0 OR a1); restore a0,a1 x-inversions after phase? keep order

    # phase: -1 iff flag == 1
    qc.z(flag)

    # uncompute flag
    qc.ccx(a0, a1, flag)
    qc.x(flag)
    qc.x(a1)
    qc.x(a0)

    # uncompute a1, a0
    qc.mcx([s[2], s[3], s[4], s[5]], a1)
    qc.mcx([s[1], s[2], s[3], s[4]], a0)
