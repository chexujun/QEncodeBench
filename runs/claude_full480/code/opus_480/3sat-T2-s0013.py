from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # clauses as list of (var_index, is_positive)
    clauses = [
        [(0, True), (2, True), (3, False)],
        [(1, False), (2, True), (4, True)],
        [(0, False), (1, True), (4, False)],
        [(1, True), (2, False), (4, False)],
        [(2, False), (3, False), (4, True)],
        [(0, False), (1, True), (2, True)],
    ]
    clause_anc = ancilla_qubits[:6]   # one ancilla per clause
    out_anc = ancilla_qubits[6]       # final AND ancilla

    def compute_clause(clause, anc):
        # clause is OR of literals. Compute clause satisfied -> anc = 1.
        # A clause (a OR b OR c) is FALSE only when all literals false.
        # literal_i false means qubit == (0 if positive else 1).
        # Flip qubits so that "all literals false" == "all controls 1",
        # then anc gets the OR via De Morgan: anc = 1 unless all-false.
        neg = []
        for (vi, pos) in clause:
            # literal is true when qubit == (1 if pos else 0).
            # We want control-active when literal is FALSE.
            # literal false when qubit == (0 if pos else 1).
            if pos:
                qc.x(x[vi])   # now qubit==1 means literal false
                neg.append(vi)
            else:
                neg.append(None)
        ctrls = [x[vi] for (vi, pos) in clause]
        # anc starts |0>; set anc=1, then if all-false flip to 0
        qc.x(anc)
        qc.mcx(ctrls, anc)
        # undo the x flips
        for (vi, pos) in clause:
            if pos:
                qc.x(x[vi])

    def uncompute_clause(clause, anc):
        for (vi, pos) in clause:
            if pos:
                qc.x(x[vi])
        ctrls = [x[vi] for (vi, pos) in clause]
        qc.mcx(ctrls, anc)
        qc.x(anc)
        for (vi, pos) in clause:
            if pos:
                qc.x(x[vi])

    # compute all clause ancillas
    for cl, anc in zip(clauses, clause_anc):
        compute_clause(cl, anc)
    # AND of all clause ancillas -> out_anc
    qc.mcx(clause_anc, out_anc)
    # phase
    qc.z(out_anc)
    # uncompute AND
    qc.mcx(clause_anc, out_anc)
    # uncompute clause ancillas (reverse order)
    for cl, anc in zip(reversed(clauses), reversed(clause_anc)):
        uncompute_clause(cl, anc)
