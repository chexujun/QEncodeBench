from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Clause definitions: (qubit, negated_literal_flag)
    # Clause k is satisfied unless all its literals are false.
    # A literal (var) is false when var==0 for a positive literal, var==1 for a negated literal.
    # We compute clause-false detection: apply X to make "all literals false" -> all-ones, use ccx.
    clauses = [
        [(x0, False), (x1, False), (x2, False)],  # (x0 OR x1 OR x2)
        [(x0, True),  (x1, False), (x2, True)],   # (NOT x0 OR x1 OR NOT x2)
        [(x0, True),  (x1, True),  (x2, True)],   # (NOT x0 OR NOT x1 OR NOT x2)
        [(x0, False), (x1, False), (x2, True)],   # (x0 OR x1 OR NOT x2)
        [(x0, False), (x1, True),  (x2, False)],  # (x0 OR NOT x1 OR x2)
    ]

    def clause_compute(lits, target):
        # target flips to |1> iff the clause is SATISFIED.
        # First set target = 1 unconditionally, then subtract the all-false case.
        # A literal is TRUE when: positive literal and var==1, or negated literal and var==0.
        # Clause is FALSE iff every literal is false.
        # Literal false condition: positive -> var==0 ; negated -> var==1.
        # Map each qubit so that "literal false" corresponds to control==1.
        # positive literal false when var==0 -> apply X so that ==1 marks false.
        # negated literal false when var==1 -> control==1 directly.
        for (q, neg) in lits:
            if not neg:
                qc.x(q)
        # Now for every literal, control==1 means that literal is false.
        qs = [q for (q, neg) in lits]
        # target ^= (all literals false)
        qc.mcx(qs, target)
        # target currently = (clause false). Flip to (clause satisfied).
        qc.x(target)
        # undo the X on positive literals
        for (q, neg) in lits:
            if not neg:
                qc.x(q)

    def clause_uncompute(lits, target):
        for (q, neg) in lits:
            if not neg:
                qc.x(q)
        qc.x(target)
        qs = [q for (q, neg) in lits]
        qc.mcx(qs, target)
        for (q, neg) in lits:
            if not neg:
                qc.x(q)

    # Compute each clause satisfaction into a dedicated ancilla c[k]
    for k in range(5):
        clause_compute(clauses[k], c[k])

    # out flips iff all 5 clause ancillas are 1 (formula satisfied)
    qc.mcx(c, out)
    qc.z(out)
    qc.mcx(c, out)

    # Uncompute clauses
    for k in reversed(range(5)):
        clause_uncompute(clauses[k], c[k])
