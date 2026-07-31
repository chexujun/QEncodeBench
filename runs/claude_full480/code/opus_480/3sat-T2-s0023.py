import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # Clause definitions: (index, negated?) literals.
    clauses = [
        [(0, True), (1, False), (4, True)],
        [(0, True), (1, False), (2, False)],
        [(0, False), (3, True), (4, True)],
        [(1, False), (2, False), (3, False)],
        [(0, True), (2, True), (4, True)],
        [(0, True), (2, True), (4, False)],
    ]

    def flips(clause):
        # A clause (l0 OR l1 OR l2) is FALSE iff every literal is false.
        # Literal (i, neg): false when x_i == (neg? 1 : 0).
        # We X-flip so that the "all false" case maps to all-ones for a ccx/mcx.
        f = []
        for (i, neg) in clause:
            # literal false when qubit == (1 if neg else 0).
            # want controls to be 1 when literal is false -> if literal false at qubit==0, add X.
            if not neg:
                f.append(x[i])
        return f

    def compute_clause(clause, target):
        # Set target = 1 iff clause satisfied.
        # First compute "clause unsatisfied" into target via mcx over the
        # all-false condition, then X to invert.
        fl = flips(clause)
        for q in fl:
            qc.x(q)
        ctrls = [x[i] for (i, neg) in clause]
        qc.mcx(ctrls, target)   # target ^= (all controls == 1) == (clause unsat)
        for q in fl:
            qc.x(q)
        qc.x(target)            # target = clause satisfied

    def uncompute_clause(clause, target):
        qc.x(target)
        fl = flips(clause)
        for q in fl:
            qc.x(q)
        ctrls = [x[i] for (i, neg) in clause]
        qc.mcx(ctrls, target)
        for q in fl:
            qc.x(q)

    # Compute each clause result into its ancilla.
    for k, clause in enumerate(clauses):
        compute_clause(clause, cl[k])

    # out = AND of all clause ancillas.
    qc.mcx(cl, out)

    # Phase.
    qc.z(out)

    # Uncompute.
    qc.mcx(cl, out)
    for k, clause in enumerate(clauses):
        uncompute_clause(clause, cl[k])
