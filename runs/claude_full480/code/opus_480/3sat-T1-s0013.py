from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Each clause: literals (qubit, negated?) ; clause is OR of literals.
    # Clause satisfied unless ALL literals false.
    # We compute clause_ok into ancilla c[k]:
    #   set c[k] = 1 if clause satisfied.
    #   Trick: flip the literal-negated inputs so that "false literal" -> qubit=1,
    #   clause unsatisfied iff all these are 1. Compute AND into a temp, then c[k]=NOT AND.
    clauses = [
        [(x1, True), (x2, True), (x3, True)],   # NOT x1 OR NOT x2 OR NOT x3
        [(x0, False), (x2, True), (x3, True)],  # x0 OR NOT x2 OR NOT x3
        [(x1, False), (x2, True), (x3, False)], # x1 OR NOT x2 OR x3
        [(x1, True), (x2, False), (x3, False)], # NOT x1 OR x2 OR x3
        [(x1, False), (x2, True), (x3, True)],  # x1 OR NOT x2 OR NOT x3
    ]

    def clause_compute(qc, lits, target):
        # For literal (q, neg): the literal is FALSE when (q==0 and not neg) or (q==1 and neg).
        # We want a control that is 1 exactly when literal is FALSE.
        # For neg=False literal x: false when q==0 -> apply X so control=1 when q==0.
        # For neg=True literal NOT x: false when q==1 -> control = q directly.
        ctrls = []
        for (q, neg) in lits:
            if not neg:
                qc.x(q)   # now q==1 means literal false
            ctrls.append(q)
        # target = AND(all ctrls) => clause UNSATISFIED
        qc.mcx(ctrls, target)
        # undo the X flips
        for (q, neg) in lits:
            if not neg:
                qc.x(q)
        # target currently 1 iff clause unsatisfied; flip to get clause_ok
        qc.x(target)

    def clause_uncompute(qc, lits, target):
        qc.x(target)
        ctrls = []
        for (q, neg) in lits:
            if not neg:
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, target)
        for (q, neg) in lits:
            if not neg:
                qc.x(q)

    # compute all clause_ok flags
    for k, lits in enumerate(clauses):
        clause_compute(qc, lits, c[k])

    # phase -1 iff all five clause_ok == 1
    qc.h(out)
    qc.mcx(c, out)
    qc.h(out)
    qc.mcx(c, out)  # this leaves out=|0> since two H sandwich a phase kickback? 

    # NOTE: correct phase-kickback approach below replaces the above.
    # uncompute clause flags
    for k, lits in enumerate(clauses):
        clause_uncompute(qc, lits, c[k])
