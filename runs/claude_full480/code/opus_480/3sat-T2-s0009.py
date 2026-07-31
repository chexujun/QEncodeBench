from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]

    # Clauses: (literal, negated?) triples. A clause is satisfied unless all
    # literals are false. We compute an ancilla = 1 iff the clause is SATISFIED.
    # Encoding: for literal x_i (positive), false means qubit==0; for NOT x_i,
    # false means qubit==1. Clause unsatisfied iff every literal is false.
    # We set clause_anc to 1 when satisfied by: flip the "all-false" pattern to
    # all-ones, mcx into ancilla, giving anc=1 for the unsatisfied assignment,
    # then X on ancilla -> anc=1 iff satisfied.

    clauses = [
        [(x0, True), (x1, False), (x3, False)],   # (NOT x0 OR x1 OR x3)
        [(x0, False), (x1, False), (x2, True)],   # (x0 OR x1 OR NOT x2)
        [(x0, True), (x1, False), (x2, True)],    # (NOT x0 OR x1 OR NOT x2)
        [(x1, True), (x2, False), (x3, False)],   # (NOT x1 OR x2 OR x3)
        [(x0, True), (x1, True), (x2, False)],    # (NOT x0 OR NOT x1 OR x2)
    ]

    clause_anc = ancilla_qubits[0:5]
    out = ancilla_qubits[5]

    def compute():
        for (lits, canc) in zip(clauses, clause_anc):
            # A literal is TRUE when: positive literal and qubit==1, or
            # negative literal and qubit==0. Clause unsatisfied iff all false,
            # i.e. positive lits qubit==0 and negative lits qubit==1.
            # Map "false" state to |1> on each qubit via X, then mcx = all-false.
            ctrls = []
            for (q, negated) in lits:
                # literal false condition: positive -> q==0 ; negative -> q==1
                if not negated:
                    qc.x(q)  # now q==1 means literal false
                ctrls.append(q)
            qc.mcx(ctrls, canc)  # canc = 1 iff clause unsatisfied
            for (q, negated) in lits:
                if not negated:
                    qc.x(q)  # restore
            qc.x(canc)  # canc = 1 iff clause satisfied

    compute()
    # out = AND of all clause_anc (all satisfied)
    qc.mcx(clause_anc, out)
    qc.z(out)
    qc.mcx(clause_anc, out)

    # uncompute clause ancillas (mirror)
    for (lits, canc) in reversed(list(zip(clauses, clause_anc))):
        qc.x(canc)
        ctrls = []
        for (q, negated) in lits:
            if not negated:
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, canc)
        for (q, negated) in lits:
            if not negated:
                qc.x(q)
