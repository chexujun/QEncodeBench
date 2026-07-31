import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])
    # clause ancillas c0..c4 (one per clause), final flag ancilla f
    c = ancilla_qubits[0:5]
    f = ancilla_qubits[5]

    # Each clause is an OR of 3 literals. A clause is FALSE iff all its
    # literals are false. We compute clause-ancilla = clause_value using:
    #   set literals to their "false" polarity, AND them into ancilla via
    #   x-gate trick: ancilla starts |0>; we compute NOT(all-literals-false).
    # We compute clause = 1 (satisfied) into c[k].

    # Definition of clauses as (qubit, negated?) triples.
    # literal True means variable matches; for "NOT x" negated=True.
    clauses = [
        [(x0, True), (x1, False), (x3, False)],   # NOT x0 OR x1 OR x3
        [(x0, True), (x1, False), (x2, True)],    # NOT x0 OR x1 OR NOT x2
        [(x0, False), (x1, True), (x3, False)],   # x0 OR NOT x1 OR x3
        [(x0, True), (x2, False), (x3, False)],   # NOT x0 OR x2 OR x3
        [(x0, True), (x1, True), (x3, True)],     # NOT x0 OR NOT x1 OR NOT x3
    ]

    def compute_clause(lits, target):
        # A literal is satisfied when qubit == (0 if negated else 1).
        # Clause satisfied = OR of literals. Clause FALSE iff every literal
        # is unsatisfied, i.e. every qubit equals its "false" value.
        # We build: flip qubits so that "clause false" <-> all controls 1,
        # mcx onto target => target=1 when clause false, then X target.
        false_vals = []  # qubit value that makes the literal false
        for (q, neg) in lits:
            false_vals.append((q, 1 if neg else 0))
        # For an mcx that triggers when all literals false, controls must
        # be |1> at the false configuration. If false value is 0, pre-X it.
        for (q, fv) in false_vals:
            if fv == 0:
                target_q = q
                # bring to 1 when false
                # placeholder handled below
        # apply pre-X on qubits whose false value is 0
        for (q, fv) in false_vals:
            if fv == 0:
                qc.x(q)
        ctrls = [q for (q, fv) in false_vals]
        qc.mcx(ctrls, target)   # target = 1 iff clause is FALSE
        # undo pre-X
        for (q, fv) in false_vals:
            if fv == 0:
                qc.x(q)
        qc.x(target)            # target = 1 iff clause is TRUE

    def uncompute_clause(lits, target):
        false_vals = [(q, 1 if neg else 0) for (q, neg) in lits]
        qc.x(target)
        for (q, fv) in false_vals:
            if fv == 0:
                qc.x(q)
        ctrls = [q for (q, fv) in false_vals]
        qc.mcx(ctrls, target)
        for (q, fv) in false_vals:
            if fv == 0:
                qc.x(q)

    # compute all clause ancillas
    for k, cl in enumerate(clauses):
        compute_clause(cl, c[k])

    # f = AND of all clause ancillas
    qc.mcx(c, f)
    qc.z(f)
    qc.mcx(c, f)

    # uncompute clause ancillas (reverse order)
    for k in reversed(range(len(clauses))):
        uncompute_clause(clauses[k], c[k])
