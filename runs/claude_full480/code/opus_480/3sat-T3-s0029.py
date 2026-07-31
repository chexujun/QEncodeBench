from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    # Clauses as lists of (var_index, is_negated) literals.
    # Clause is satisfied unless ALL literals are false.
    # Literal l = (i, neg): literal true when qubit == (0 if neg else 1).
    clauses = [
        [(1, False), (4, True), (5, False)],
        [(0, False), (1, False), (2, False)],
        [(1, False), (2, True), (5, True)],
        [(3, False), (4, True), (5, False)],
        [(0, False), (4, False), (5, True)],
        [(1, True), (4, True), (5, False)],
        [(0, True), (1, False), (2, False)],
    ]
    n = len(clauses)
    clause_anc = ancilla_qubits[:n]      # one ancilla per clause
    target = ancilla_qubits[n]           # phase target ancilla

    def compute_clause(cl, anc):
        # Set anc = 1 iff clause satisfied.
        # Clause unsatisfied iff every literal false: qubit == neg.
        # For a positive literal (neg False), literal false when qubit==0.
        # For a negative literal (neg True), literal false when qubit==1.
        # Flip control qubits so that "all false" -> all controls = 1.
        ctrls = []
        for (i, neg) in cl:
            if not neg:
                qc.x(p[i])   # positive literal false when qubit=0 -> make it 1
            ctrls.append(p[i])
        # Now anc_pre = 1 iff all literals false (clause unsatisfied)
        qc.mcx(ctrls, anc)
        # Undo flips
        for (i, neg) in cl:
            if not neg:
                qc.x(p[i])
        # anc currently = clause_unsatisfied; invert to clause_satisfied
        qc.x(anc)

    def uncompute_clause(cl, anc):
        qc.x(anc)
        ctrls = []
        for (i, neg) in cl:
            if not neg:
                qc.x(p[i])
            ctrls.append(p[i])
        qc.mcx(ctrls, anc)
        for (i, neg) in cl:
            if not neg:
                qc.x(p[i])

    for cl, anc in zip(clauses, clause_anc):
        compute_clause(cl, anc)

    qc.h(target)
    qc.x(target)
    qc.mcx(clause_anc, target)
    qc.x(target)
    qc.h(target)

    for cl, anc in reversed(list(zip(clauses, clause_anc))):
        uncompute_clause(cl, anc)
