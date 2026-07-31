from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits):
    # Variables: x0..x5 on problem_qubits[0..5]; basis 1 == True.
    # Clauses (each a 3-literal OR). A clause is UNSAT iff all three literals
    # are False. We compute, for each clause, an ancilla that is 1 iff the
    # clause is SATISFIED, then multi-control on all clause-ancillas == 1.
    #
    # For a literal:
    #   positive literal x_i : True when qubit == 1
    #   negative literal ~x_i: True when qubit == 0
    # A clause (l_a OR l_b OR l_c) is FALSE iff every literal is False.
    # We compute clause_sat = OR of literals = NOT(AND of negations).
    #
    # Implementation per clause: bring each literal's qubit to a form where
    # "literal is False" == |1>, take the AND (mcx) into the clause ancilla to
    # detect the all-False case, then X the ancilla so it holds clause_sat.
    #
    # For a positive literal x_i, "literal False" == qubit 0, so we X the qubit
    #   (temporarily) to map False->1. For a negative literal ~x_i, "literal
    #   False" == qubit 1, so no flip needed. We undo the temp flips right after.

    p = problem_qubits

    # clause definitions: list of (qubit_index, is_positive_literal)
    clauses = [
        [(1, False), (3, False), (4, False)],   # (~x1 | ~x3 | ~x4)
        [(3, False), (4, False), (5, True)],     # (~x3 | ~x4 |  x5)
        [(0, False), (2, False), (5, False)],    # (~x0 | ~x2 | ~x5)
        [(0, True),  (1, True),  (3, False)],     # ( x0 |  x1 | ~x3)
        [(2, False), (4, True),  (5, True)],      # (~x2 |  x4 |  x5)
    ]

    clause_anc = ancilla_qubits[:len(clauses)]

    def compute_clauses():
        for ci, lits in enumerate(clauses):
            a = clause_anc[ci]
            ctrls = []
            flips = []
            for (qi, pos) in lits:
                # want control qubit to be 1 when the literal is FALSE
                # positive literal false <=> qubit 0 -> flip
                # negative literal false <=> qubit 1 -> no flip
                if pos:
                    qc.x(p[qi])
                    flips.append(p[qi])
                ctrls.append(p[qi])
            # a := AND(all literals false)  (a currently |0>)
            qc.mcx(ctrls, a)
            # undo temp flips
            for q in flips:
                qc.x(q)
            # a now = 1 iff clause UNSAT; convert to clause_sat
            qc.x(a)

    # compute
    compute_clauses()

    # phase: -1 iff all clauses satisfied (all clause_anc == 1)
    qc.h(clause_anc[-1])
    qc.mcx(clause_anc[:-1], clause_anc[-1])
    qc.h(clause_anc[-1])

    # uncompute clauses (mirror)
    for ci in reversed(range(len(clauses))):
        lits = clauses[ci]
        a = clause_anc[ci]
        qc.x(a)
        ctrls = []
        flips = []
        for (qi, pos) in lits:
            if pos:
                qc.x(p[qi])
                flips.append(p[qi])
            ctrls.append(p[qi])
        qc.mcx(ctrls, a)
        for q in flips:
            qc.x(q)
