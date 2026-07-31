from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    # clauses as list of (qubit, negated) literals; clause satisfied unless all literals false
    clauses = [
        [(x0, True), (x1, False), (x2, True)],
        [(x0, True), (x1, False), (x2, False)],
        [(x0, False), (x1, False), (x2, True)],
        [(x0, True), (x1, True), (x2, False)],
    ]
    clause_anc = ancilla_qubits[:4]
    out_anc = ancilla_qubits[4]

    def flips(clause):
        # a literal is TRUE when qubit == (0 if negated else 1)
        # clause is FALSE iff every literal is false; literal false when qubit == (1 if negated else 0)
        # we set X on qubits so that "all literals false" maps to "all controls =1"
        fl = []
        for (q, neg) in clause:
            # literal false condition: q == (1 if neg else 0)
            # we want control-active(=1) when literal is false -> apply X if false-cond is q==0
            if not neg:
                fl.append(q)  # literal false when q==0 -> X so it becomes 1
        # for neg literals, false when q==1 -> already 1, no X
        return fl

    # compute each clause ancilla = 1 iff clause satisfied
    for i, clause in enumerate(clauses):
        ctrls = [q for (q, _) in clause]
        fl = flips(clause)
        for q in fl:
            qc.x(q)
        # now clause-false <=> all ctrls == 1
        qc.mcx(ctrls, clause_anc[i])  # clause_anc = 1 iff clause false
        for q in fl:
            qc.x(q)
        qc.x(clause_anc[i])  # clause_anc = 1 iff clause satisfied

    # out_anc = AND of all clause_anc (formula satisfied)
    qc.mcx(clause_anc, out_anc)
    qc.z(out_anc)
    qc.mcx(clause_anc, out_anc)

    # uncompute clause ancillas
    for i, clause in enumerate(clauses):
        ctrls = [q for (q, _) in clause]
        fl = flips(clause)
        qc.x(clause_anc[i])
        for q in fl:
            qc.x(q)
        qc.mcx(ctrls, clause_anc[i])
        for q in fl:
            qc.x(q)
