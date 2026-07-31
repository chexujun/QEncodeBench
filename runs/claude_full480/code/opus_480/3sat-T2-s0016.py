import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]   # one ancilla per clause
    out = ancilla_qubits[6]   # final phase ancilla

    # Each clause -> ancilla = 1 iff clause satisfied.
    # Compute clause ancilla via De Morgan: clause is a 3-literal OR.
    # ancilla = OR(l0,l1,l2) = NOT(AND(NOT l0, NOT l1, NOT l2)).
    # For a literal that is a variable v, "NOT literal" = NOT v.
    # For a literal that is NOT v, "NOT literal" = v.
    # We set ancilla = 1 by X, then flip to 0 iff all three literals false.
    # all literals false means: for positive literal v -> v=0; for negative literal -> v=1.

    # clause specs: list of (qubit, polarity) polarity True=positive var, False=negated
    clauses = [
        [(x[0], False), (x[1], False), (x[3], True)],   # ~x0 | ~x1 | x3
        [(x[1], True), (x[4], True), (x[5], False)],    # x1 | x4 | ~x5
        [(x[1], True), (x[2], True), (x[3], True)],     # x1 | x2 | x3
        [(x[0], False), (x[1], False), (x[4], False)],  # ~x0 | ~x1 | ~x4
        [(x[0], False), (x[1], False), (x[2], False)],  # ~x0 | ~x1 | ~x2
        [(x[1], False), (x[3], True), (x[4], False)],   # ~x1 | x3 | ~x4
    ]

    def compute_clause(spec, anc):
        # anc starts at |0>. Set anc=1.
        qc.x(anc)
        # We want to flip anc to 0 iff all literals false.
        # "literal false" condition: positive literal false <=> var==0 ; negative literal false <=> var==1.
        # mcx fires when all controls are 1. Arrange controls so that "1" means literal-false.
        # positive literal: literal-false <=> var==0 -> need to X the var first.
        ctrls = []
        pos_flipped = []
        for (q, pol) in spec:
            if pol:  # positive literal: false when var==0 -> flip so control high means var==0
                qc.x(q)
                pos_flipped.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, anc)
        for q in pos_flipped:
            qc.x(q)

    def uncompute_clause(spec, anc):
        ctrls = []
        pos_flipped = []
        for (q, pol) in spec:
            if pol:
                qc.x(q)
                pos_flipped.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, anc)
        for q in pos_flipped:
            qc.x(q)
        qc.x(anc)

    # compute all clause ancillas
    for spec, anc in zip(clauses, cl):
        compute_clause(spec, anc)

    # formula satisfied iff all clause ancillas == 1 -> phase -1
    qc.h(out)
    qc.x(out)
    qc.mcx(cl, out)
    qc.x(out)
    qc.h(out)

    # uncompute clause ancillas (reverse order)
    for spec, anc in reversed(list(zip(clauses, cl))):
        uncompute_clause(spec, anc)
