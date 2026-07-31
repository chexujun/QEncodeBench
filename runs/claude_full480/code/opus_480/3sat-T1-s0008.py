from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c0, c1, c2, c3, c4 = (ancilla_qubits[0], ancilla_qubits[1],
                          ancilla_qubits[2], ancilla_qubits[3],
                          ancilla_qubits[4])
    out = ancilla_qubits[5]

    # Each clause -> clause ancilla = 1 iff clause satisfied.
    # A clause (l_a OR l_b OR l_c) is satisfied unless all three literals are false.
    # Compute NOT(all literals false): set literals so that "false" means qubit==0,
    # then use X-conditioning to build the AND of negations, flip.

    def clause(anc, lits):
        # lits: list of (qubit, negated) where negated=True means literal is NOT x.
        # literal is TRUE when: (qubit==1 if not negated) or (qubit==0 if negated).
        # literal is FALSE when qubit == (0 if not negated else 1).
        # We want anc = OR of literals = NOT(AND of literal-false).
        # literal false condition: qubit == v_false, where v_false = 0 if not negated else 1.
        # Map each qubit to be 1 when its literal is FALSE: apply X if v_false==0.
        ctrls = []
        flips = []
        for (q, neg) in lits:
            v_false = 1 if neg else 0
            if v_false == 0:
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        # anc currently 0; set anc=1 if all-false (AND)
        qc.mcx(ctrls, anc)
        # anc = all-false; we want OR = NOT all-false
        qc.x(anc)
        for q in flips:
            qc.x(q)

    def unclause(anc, lits):
        flips = []
        ctrls = []
        for (q, neg) in lits:
            v_false = 1 if neg else 0
            if v_false == 0:
                flips.append(q)
            ctrls.append(q)
        for q in flips:
            qc.x(q)
        qc.x(anc)
        qc.mcx(ctrls, anc)
        for q in flips:
            qc.x(q)

    cl0 = [(x0, True), (x1, False), (x2, True)]
    cl1 = [(x1, True), (x2, False), (x3, True)]
    cl2 = [(x1, True), (x2, True), (x3, True)]
    cl3 = [(x1, False), (x2, False), (x3, True)]
    cl4 = [(x0, False), (x2, True), (x3, True)]

    clause(c0, cl0)
    clause(c1, cl1)
    clause(c2, cl2)
    clause(c3, cl3)
    clause(c4, cl4)

    # phase -1 iff all 5 clause ancillas are 1
    qc.h(out)
    qc.x(out)
    qc.mcx([c0, c1, c2, c3, c4], out)
    qc.x(out)
    qc.h(out)

    unclause(c4, cl4)
    unclause(c3, cl3)
    unclause(c2, cl2)
    unclause(c1, cl1)
    unclause(c0, cl0)
