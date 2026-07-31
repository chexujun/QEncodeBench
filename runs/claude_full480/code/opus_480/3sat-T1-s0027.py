from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Clauses as (qubit, negated?) triples. A clause literal is satisfied when
    # (qubit value) XOR negated == 1 semantics handled by pre/post X flips.
    # clause = OR of literals; ancilla c[k] = 1 iff clause k satisfied.
    # Compute NOT(clause) = AND of negated literals via mcx on complemented lits,
    # then flip c[k].
    clauses = [
        [(x0, False), (x1, False), (x2, True)],   # x0 OR x1 OR NOT x2
        [(x0, True),  (x1, False), (x2, True)],   # NOT x0 OR x1 OR NOT x2
        [(x0, True),  (x2, True),  (x3, True)],   # NOT x0 OR NOT x2 OR NOT x3
        [(x0, False), (x1, True),  (x2, True)],   # x0 OR NOT x1 OR NOT x2
        [(x0, True),  (x1, False), (x2, False)],  # NOT x0 OR x1 OR x2
    ]

    def clause_compute(k, cl):
        # Set X on qubits so that "literal false" corresponds to |1>.
        # literal (q, neg): satisfied iff val==1 (neg False) or val==0 (neg True).
        # literal false when: neg False -> val==0 ; neg True -> val==1.
        # We want mcx to fire iff ALL literals false (clause unsat).
        # Put each control into |1> when its literal is FALSE:
        #   neg False (need val==0 for false): apply X so val==0 -> control 1.
        #   neg True  (need val==1 for false): no X, control already 1 when val==1.
        flips = [q for (q, neg) in cl if not neg]
        for q in flips:
            qc.x(q)
        ctrls = [q for (q, _) in cl]
        qc.mcx(ctrls, c[k])   # c[k] = 1 iff clause unsatisfied
        for q in flips:
            qc.x(q)
        qc.x(c[k])            # c[k] = 1 iff clause satisfied

    # Compute all clause ancillas
    for k, cl in enumerate(clauses):
        clause_compute(k, cl)

    # out = AND of all clause ancillas
    qc.mcx(c, out)
    qc.z(out)
    qc.mcx(c, out)

    # Uncompute clause ancillas (mirror)
    for k in reversed(range(len(clauses))):
        cl = clauses[k]
        qc.x(c[k])
        flips = [q for (q, neg) in cl if not neg]
        ctrls = [q for (q, _) in cl]
        for q in flips:
            qc.x(q)
        qc.mcx(ctrls, c[k])
        for q in flips:
            qc.x(q)
