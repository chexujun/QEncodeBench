from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    c = ancilla_qubits  # 6 ancillas: c[0..4] per-clause, c[5] final phase target

    # Clause i is satisfied -> c[i] = 1.
    # A 3-literal clause (l_a OR l_b OR l_c) is FALSE iff all three literals are False.
    # Compute NOT(clause) via mcx on the "all literals false" condition, then flip c[i].
    # A positive literal x is False when x==0; a negative literal NOT x is False when x==1.

    def clause(target, lits):
        # lits: list of (qubit, negated) ; literal is False when (qubit == (0 if not negated else 1))
        # We want target = 1 if clause satisfied. Start target=1, set to 0 if all literals false.
        # Flip control qubits so that "literal false" -> control==1, then mcx sets target,
        # then we x(target) so target=1 when NOT all-false.
        flips = []
        for q, neg in lits:
            if not neg:
                # positive literal false when q==0 -> flip so control==1 when q==0
                qc.x(q)
                flips.append(q)
            else:
                # negative literal false when q==1 -> control already 1 when q==1, no flip
                pass
        qc.mcx([q for q, _ in lits], target)  # target ^= (all controls ==1) == all literals false
        qc.x(target)                          # target = 1 iff clause satisfied
        for q in flips:
            qc.x(q)

    clauses = [
        [(x0, False), (x1, True), (x4, False)],   # (x0 OR NOT x1 OR x4)
        [(x2, True), (x3, True), (x4, True)],     # (NOT x2 OR NOT x3 OR NOT x4)
        [(x0, False), (x3, True), (x4, False)],   # (x0 OR NOT x3 OR x4)
        [(x1, False), (x2, False), (x4, True)],   # (x1 OR x2 OR NOT x4)
        [(x0, False), (x2, False), (x4, True)],   # (x0 OR x2 OR NOT x4)
    ]

    # compute clause satisfaction flags
    for i, cl in enumerate(clauses):
        clause(c[i], cl)

    # phase -1 iff all clause flags are 1
    qc.h(c[5])
    qc.mcx([c[0], c[1], c[2], c[3], c[4]], c[5])
    qc.h(c[5])

    # uncompute clause flags (mirror)
    for i, cl in reversed(list(enumerate(clauses))):
        # inverse of clause(): x(target); mcx; x flips  -- reverse the operations
        flips = []
        for q, neg in cl:
            if not neg:
                qc.x(q)
                flips.append(q)
        qc.x(c[i])
        qc.mcx([q for q, _ in cl], c[i])
        for q in flips:
            qc.x(q)
