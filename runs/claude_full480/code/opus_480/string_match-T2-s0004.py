from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "001010"
    # offset o in 0..1: pattern position i compared against s_(o+i)
    # match_o = AND over i of (s_(o+i) == pattern[i])   (wildcards skipped)
    # f = match_0 OR match_1
    # Use De Morgan on OR of two ANDs via ancillas a0, a1 and a target a2.
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]

    def compute_match(offset, anc):
        # For bits that must equal 0, flip so that "match" needs the qubit=1.
        flips = []
        controls = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[offset + i]
            controls.append(q)
            if ch == '0':
                flips.append(q)
        for q in flips:
            qc.x(q)
        qc.mcx(controls, anc)
        for q in flips:
            qc.x(q)

    def uncompute_match(offset, anc):
        compute_match(offset, anc)  # self-inverse mirror

    # Compute both matches
    compute_match(0, a0)
    compute_match(1, a1)

    # a2 = a0 OR a1  via De Morgan: NOT( (NOT a0) AND (NOT a1) )
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.ccx(a0, a1, a2)
    qc.x(a0)
    qc.x(a1)

    # phase flip iff a2 == 1 (i.e. OR is true)
    qc.z(a2)

    # uncompute a2
    qc.x(a0)
    qc.x(a1)
    qc.ccx(a0, a1, a2)
    qc.x(a2)
    qc.x(a0)
    qc.x(a1)

    # uncompute matches
    uncompute_match(1, a1)
    uncompute_match(0, a0)
