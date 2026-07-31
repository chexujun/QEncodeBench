from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])
    # Clauses as lists of (qubit, negated?) literals.
    # A clause (l0 OR l1 OR l2) is satisfied unless all literals are false.
    # Compute clause-satisfied bit into an ancilla:
    #   set ancilla = 1 (satisfied), then flip to 0 iff all literals false.
    # "literal false" for a positive literal x means x==0; for NOT x means x==1.
    clauses = [
        [(x0, False), (x1, True),  (x3, True)],   # x0 OR NOT x1 OR NOT x3
        [(x0, False), (x1, False), (x3, True)],   # x0 OR x1 OR NOT x3
        [(x1, False), (x2, False), (x3, False)],  # x1 OR x2 OR x3
        [(x0, True),  (x1, True),  (x3, False)],  # NOT x0 OR NOT x1 OR x3
        [(x0, True),  (x1, True),  (x2, False)],  # NOT x0 OR NOT x1 OR x2
    ]

    clause_ancillas = ancilla_qubits[:5]
    final_ancilla = ancilla_qubits[5]

    def compute_clause(clause, anc):
        ctrls = [c for (c, _) in clause]
        # For "all literals false": positive literal false means qubit==0,
        # negative literal false means qubit==1. We want a control-on-those.
        # Flip qubits whose "false" condition is qubit==0 so that the
        # all-false pattern maps to all-ones, then mcx, then unflip.
        flips = []
        for (c, neg) in clause:
            # literal false condition: positive -> c==0 ; negative -> c==1
            if not neg:
                flips.append(c)  # need c==0 to be "false", flip so ==1
        for c in flips:
            qc.x(c)
        # ancilla currently |0>; set to satisfied=1
        qc.x(anc)
        # if all literals false (all controls now ==1) -> flip anc to 0
        qc.mcx(ctrls, anc)
        for c in flips:
            qc.x(c)

    def uncompute_clause(clause, anc):
        ctrls = [c for (c, _) in clause]
        flips = [c for (c, neg) in clause if not neg]
        for c in flips:
            qc.x(c)
        qc.mcx(ctrls, anc)
        qc.x(anc)
        for c in flips:
            qc.x(c)

    # Compute all clause bits.
    for cl, anc in zip(clauses, clause_ancillas):
        compute_clause(cl, anc)

    # Phase -1 iff all clause bits are 1 (formula satisfied).
    qc.h(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)
    qc.h(final_ancilla)

    # Uncompute clause bits (mirror).
    for cl, anc in zip(clauses, clause_ancillas):
        uncompute_clause(cl, anc)
