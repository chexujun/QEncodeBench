import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    # One ancilla per clause; the clause-ancilla stores whether the clause is FALSE.
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # A clause (l0 OR l1 OR l2) is FALSE iff every literal is false.
    # For a positive literal x_i, "literal false" means x_i == 0.
    # For a negative literal NOT x_i, "literal false" means x_i == 1.
    # We compute clause-false into the clause ancilla using an mcx whose
    # controls are the problem qubits, with X applied first to those problem
    # qubits whose literal is POSITIVE (so control-on-1 detects literal-false).
    #
    # clauses as (var, is_negative) triples:
    clauses = [
        [(0, False), (1, True), (2, False)],   # x0 OR NOT x1 OR x2
        [(0, True), (1, True), (2, False)],    # NOT x0 OR NOT x1 OR x2
        [(0, True), (1, True), (2, True)],     # NOT x0 OR NOT x1 OR NOT x2
        [(0, False), (1, True), (2, True)],    # x0 OR NOT x1 OR NOT x2
        [(0, False), (1, False), (2, True)],   # x0 OR x1 OR NOT x2
    ]

    def clause_compute(clause, target):
        # Flip problem qubits whose literal is positive, so that a control
        # on |1> corresponds to that literal being false.
        flips = [problem_qubits[v] for (v, neg) in clause if not neg]
        ctrls = [problem_qubits[v] for (v, neg) in clause]
        for q in flips:
            qc.x(q)
        qc.mcx(ctrls, target)   # target ^= (all literals false) = clause FALSE
        for q in flips:
            qc.x(q)

    # Compute clause-false flags.
    for clause, target in zip(clauses, c):
        clause_compute(clause, target)

    # Formula satisfied iff NO clause is false, i.e. all clause ancillas == 0.
    # Flip clause ancillas so control-on-1 means clause satisfied, then AND.
    for cc in c:
        qc.x(cc)
    qc.mcx(c, out)   # out = 1 iff all clauses satisfied
    for cc in c:
        qc.x(cc)

    # Phase.
    qc.z(out)

    # Uncompute out.
    for cc in c:
        qc.x(cc)
    qc.mcx(c, out)
    for cc in c:
        qc.x(cc)

    # Uncompute clause flags (mirror).
    for clause, target in zip(reversed(clauses), reversed(c)):
        clause_compute(clause, target)
