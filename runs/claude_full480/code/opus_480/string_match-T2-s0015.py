from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern "?11": position 0 wildcard, positions 1 and 2 require value 1.
    # Text length 5, offsets o in 0..2. Match at offset o iff
    # s_(o+1) == 1 AND s_(o+2) == 1.
    # offset 0 -> s1 & s2 ; offset 1 -> s2 & s3 ; offset 2 -> s3 & s4.
    # f = m0 OR m1 OR m2, where m_o = s_(o+1) AND s_(o+2).

    s = problem_qubits
    # ancilla layout
    m = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]  # per-offset match flags
    orflag = ancilla_qubits[3]                                     # OR aggregate

    match_pairs = [(s[1], s[2]), (s[2], s[3]), (s[3], s[4])]

    # compute per-offset AND flags
    for (a, b), mm in zip(match_pairs, m):
        qc.ccx(a, b, mm)

    # compute OR of the three flags into orflag via De Morgan:
    # orflag = NOT( AND(NOT m0, NOT m1, NOT m2) )
    for mm in m:
        qc.x(mm)
    qc.mcx(m, orflag)   # orflag = m0'&m1'&m2'
    qc.x(orflag)        # orflag = OR
    for mm in m:
        qc.x(mm)

    # phase: -1 iff orflag == 1
    qc.z(orflag)

    # uncompute OR
    for mm in m:
        qc.x(mm)
    qc.x(orflag)
    qc.mcx(m, orflag)
    for mm in m:
        qc.x(mm)

    # uncompute per-offset AND flags
    for (a, b), mm in zip(match_pairs, m):
        qc.ccx(a, b, mm)
