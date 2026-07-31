import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:10]   # one ancilla per clause
    out = ancilla_qubits[10]   # final phase-marking ancilla

    # Each clause = (a OR b OR c). We set clause ancilla = OR of literals.
    # OR via De Morgan: OR = NOT(AND of negated literals).
    # literal True means we want that variable value; a negative literal
    # (NOT x) is satisfied when the variable is 0.
    #
    # clauses: list of (qubit, is_positive)
    clauses = [
        [(2, True),  (5, True),  (6, False)],   # x2 OR x5 OR NOT x6
        [(0, False), (2, True),  (7, False)],   # NOT x0 OR x2 OR NOT x7
        [(0, False), (2, False), (4, True)],    # NOT x0 OR NOT x2 OR x4
        [(2, True),  (5, False), (6, True)],    # x2 OR NOT x5 OR x6
        [(1, True),  (5, True),  (7, True)],    # x1 OR x5 OR x7
        [(2, True),  (3, True),  (5, False)],   # x2 OR x3 OR NOT x5
        [(2, False), (4, False), (6, False)],   # NOT x2 OR NOT x4 OR NOT x6
        [(0, False), (3, True),  (7, True)],    # NOT x0 OR x3 OR x7
        [(1, False), (2, True),  (3, True)],    # NOT x1 OR x2 OR x3
        [(0, False), (3, True),  (5, True)],    # NOT x0 OR x3 OR x5
    ]

    def compute_clause(cl_idx):
        lits = clauses[cl_idx]
        anc = cl[cl_idx]
        # For each literal, flip its qubit so that "literal satisfied" == 1.
        # positive literal satisfied when var==1 -> no flip
        # negative literal satisfied when var==0 -> flip so it reads 1 when var==0
        for q, pos in lits:
            if not pos:
                qc.x(x[q])
        # Now compute AND of (NOT literal_satisfied): first negate each var view.
        # We want clause_anc = OR(sat) = NOT AND(NOT sat).
        # NOT sat = flip each control. Apply X to each, ccx into anc gives AND(NOT sat),
        # then X on anc gives OR(sat).
        ctrls = [x[q] for q, pos in lits]
        for c in ctrls:
            qc.x(c)
        qc.mcx(ctrls, anc)   # anc = AND(NOT sat)
        for c in ctrls:
            qc.x(c)
        qc.x(anc)            # anc = OR(sat) = clause satisfied
        # restore the negative-literal qubits
        for q, pos in lits:
            if not pos:
                qc.x(x[q])

    def uncompute_clause(cl_idx):
        lits = clauses[cl_idx]
        anc = cl[cl_idx]
        for q, pos in lits:
            if not pos:
                qc.x(x[q])
        qc.x(anc)
        ctrls = [x[q] for q, pos in lits]
        for c in ctrls:
            qc.x(c)
        qc.mcx(ctrls, anc)
        for c in ctrls:
            qc.x(c)
        for q, pos in lits:
            if not pos:
                qc.x(x[q])

    # compute all clause ancillas
    for i in range(len(clauses)):
        compute_clause(i)

    # phase -1 iff all clause ancillas are 1 (formula satisfied)
    # compute AND of all clause ancillas into out, apply Z, uncompute.
    qc.h(out)
    qc.mcx(cl, out)
    qc.h(out)

    # uncompute all clause ancillas (reverse order)
    for i in reversed(range(len(clauses))):
        uncompute_clause(i)
