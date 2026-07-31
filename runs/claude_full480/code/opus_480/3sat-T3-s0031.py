import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Each clause (var_index, negated_flag) with OR semantics.
    # Clause is satisfied unless all literals are false.
    # Literal (i, neg): value = x_i if neg is False, else NOT x_i.
    # We compute for each clause an ancilla = 1 iff clause is SATISFIED,
    # then multi-control on all clause ancillas to flip phase.
    clauses = [
        [(2, False), (4, False), (6, True)],
        [(0, True), (3, True), (6, True)],
        [(3, False), (4, True), (6, False)],
        [(4, True), (5, False), (6, False)],
        [(0, False), (3, False), (6, True)],
        [(2, False), (5, False), (6, False)],
        [(0, False), (5, True), (6, False)],
        [(3, True), (5, False), (6, True)],
        [(0, True), (2, False), (6, False)],
        [(2, False), (3, False), (6, True)],
        [(4, False), (5, True), (6, False)],
        [(0, False), (2, True), (5, True)],
    ]

    p = problem_qubits
    clause_ancillas = ancilla_qubits[:len(clauses)]

    def compute_clause(clause, anc):
        # anc starts at |0>. Set anc = 1 iff clause satisfied.
        # Clause unsatisfied iff every literal false.
        # Literal (i,neg): false when (neg False -> x_i==0) or (neg True -> x_i==1).
        # For each literal, prepare control qubit that is 1 when literal is FALSE.
        ctrls = []
        for (i, neg) in clause:
            if not neg:
                # literal x_i; false when x_i==0 -> flip so control=1 when false
                qc.x(p[i])
            # neg True: literal NOT x_i; false when x_i==1 -> control=x_i as is
            ctrls.append(p[i])
        # anc = 1 iff NOT(all literals false) => flip anc to 1, then subtract
        # Use: set anc=1 always, then mcx makes anc=0 when all ctrls=1 (all false).
        qc.x(anc)
        qc.mcx(ctrls, anc)
        # restore x on positive literals
        for (i, neg) in clause:
            if not neg:
                qc.x(p[i])

    # compute all clause ancillas
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # phase flip iff all clause ancillas == 1
    qc.h(clause_ancillas[-1])
    qc.mcx(clause_ancillas[:-1], clause_ancillas[-1])
    qc.h(clause_ancillas[-1])

    # uncompute all clause ancillas (mirror)
    for clause, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        compute_clause(clause, anc)
