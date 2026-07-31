import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = [ancilla_qubits[i] for i in range(5)]
    out = ancilla_qubits[5]

    # Each clause -> ancilla c[k] = 1 iff clause satisfied.
    # Clause is OR of literals; compute NOT(clause) then flip.
    # Literal True condition: positive uses qubit as-is, negative uses X-wrapped.

    # clause 0: (NOT x0 OR x2 OR x3)
    # clause 1: (x0 OR NOT x1 OR NOT x2)
    # clause 2: (NOT x0 OR NOT x1 OR NOT x2)
    # clause 3: (x0 OR NOT x1 OR x3)
    # clause 4: (x0 OR x1 OR x3)
    clauses = [
        [(x0, True), (x2, False), (x3, False)],   # NOT x0, x2, x3
        [(x0, False), (x1, True), (x2, True)],     # x0, NOT x1, NOT x2
        [(x0, True), (x1, True), (x2, True)],      # NOT x0, NOT x1, NOT x2
        [(x0, False), (x1, True), (x3, False)],    # x0, NOT x1, x3
        [(x0, False), (x1, False), (x3, False)],   # x0, x1, x3
    ]

    def compute_clause(clause, target):
        # clause satisfied unless ALL literals false.
        # literal (q, neg): neg=True means literal is NOT q -> literal false when q==1.
        # We flip target to 1 when clause satisfied.
        # Method: for each literal, make it a control that is 1 when literal is TRUE.
        # A literal (q, neg=False) is true when q==1. (q, neg=True) true when q==0 -> X wrap.
        ctrls = [q for (q, neg) in clause]
        neg_wrap = [q for (q, neg) in clause if not neg]  # positive literal true at q==1;
        # We want target=1 iff clause satisfied = NOT(all literals false).
        # all literals false: for positive literal need q==0, for negative literal need q==1.
        # Set target=1 for that "all false" config via MCX with appropriate X wraps, then X target.
        # all-false condition controls: positive literal -> q==0 (X wrap), negative -> q==1 (no wrap).
        wrap = [q for (q, neg) in clause if not neg]  # positive literals need X wrap to detect q==0
        for q in wrap:
            qc.x(q)
        qc.mcx(ctrls, target)   # target ^= 1 iff all literals false
        for q in wrap:
            qc.x(q)
        qc.x(target)            # invert -> target=1 iff clause satisfied

    def uncompute_clause(clause, target):
        qc.x(target)
        wrap = [q for (q, neg) in clause if not neg]
        ctrls = [q for (q, neg) in clause]
        for q in wrap:
            qc.x(q)
        qc.mcx(ctrls, target)
        for q in wrap:
            qc.x(q)

    for k, clause in enumerate(clauses):
        compute_clause(clause, c[k])

    qc.mcx(c, out)
    qc.z(out)
    qc.mcx(c, out)

    for k in reversed(range(len(clauses))):
        uncompute_clause(clauses[k], c[k])
