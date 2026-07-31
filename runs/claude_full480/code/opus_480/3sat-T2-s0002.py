import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    x = problem_qubits
    clause_anc = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # Each clause: (l0 OR l1 OR l2). Clause ancilla c is set to 1 iff clause satisfied.
    # We compute NOT(clause) via ANDing the negations of the literals into c through
    # a compute-flip trick: set c=1, then set c=0 iff all literals false.
    # Literal value on qubit q: positive -> q, negative -> NOT q.
    # Clause false  <=>  every literal is false.
    # Strategy: for each clause, flip the qubits so that "literal false" == qubit is |1>,
    # then MCX(all three, c) sets c=1 when all literals false, i.e. clause false.
    # Then X(c) gives c=1 iff clause satisfied. Undo the literal flips.

    clauses = [
        [(0, True), (4, True), (5, False)],
        [(2, False), (4, True), (5, False)],
        [(0, True), (1, True), (4, False)],
        [(1, False), (4, True), (5, True)],
        [(0, True), (2, False), (3, False)],
        [(1, True), (2, True), (3, True)],
    ]

    def literal_false_prep(clause):
        # Flip qubits so that basis state |1> on the qubit means the literal is FALSE.
        # positive literal (var True satisfies): literal false when var is 0 -> need to flip so 0->1 => apply X
        # negative literal (NOT var satisfies): literal false when var is 1 -> already 1 => no flip
        flips = []
        for var, positive in clause:
            if positive:
                qc.x(x[var])
                flips.append(x[var])
        return flips

    # Compute all clause ancillas
    used_flips = []
    for c_idx, clause in enumerate(clauses):
        flips = literal_false_prep(clause)
        ctrls = [x[var] for (var, _) in clause]
        qc.mcx(ctrls, clause_anc[c_idx])   # clause_anc = 1 iff all literals false (clause false)
        for q in flips:
            qc.x(q)                         # undo flips
        qc.x(clause_anc[c_idx])             # now clause_anc = 1 iff clause satisfied

    # out = AND of all clause ancillas
    qc.mcx(clause_anc, out)

    # phase
    qc.z(out)

    # uncompute out
    qc.mcx(clause_anc, out)

    # uncompute clause ancillas (mirror)
    for c_idx in reversed(range(len(clauses))):
        clause = clauses[c_idx]
        qc.x(clause_anc[c_idx])
        flips = literal_false_prep(clause)
        ctrls = [x[var] for (var, _) in clause]
        qc.mcx(ctrls, clause_anc[c_idx])
        for q in flips:
            qc.x(q)
