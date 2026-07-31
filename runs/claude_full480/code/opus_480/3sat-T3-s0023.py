from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:7]   # one ancilla per clause
    out = ancilla_qubits[7]   # final AND target

    # Each clause (a OR b OR c) is TRUE unless all three literals are false.
    # We compute clause-ancilla = clause value (1 = satisfied).
    # Strategy: set ancilla to the OR via De Morgan.
    # For literals, a negated variable NOT x means we treat controls on |0>.
    # We use: clause_anc = 1 unless (all literals false).
    # Compute "all literals false" -> flip target when that pattern holds,
    # then X the target so 1 means satisfied.

    # clause literal spec: (qubit, negated?) where negated? True means literal is (NOT x)
    # A literal is TRUE when: x==1 (not negated) or x==0 (negated).
    # The clause is FALSE only when every literal is FALSE.
    # Literal FALSE condition: x==0 (not negated) or x==1 (negated).
    # We want to detect the all-literals-false pattern with an MCX whose
    # controls fire on the "literal false" value of each variable.
    # For a positive literal (not negated), literal false <=> x==0 -> control on 0 (X-wrap).
    # For a negative literal (negated), literal false <=> x==1 -> normal control.

    clauses = [
        [(0, True),  (5, True),  (6, False)],
        [(1, False), (2, True),  (4, False)],
        [(0, True),  (2, True),  (7, True)],
        [(0, True),  (5, True),  (7, True)],
        [(0, False), (2, False), (5, False)],
        [(4, True),  (6, True),  (7, True)],
        [(2, False), (6, True),  (7, True)],
    ]

    def clause_controls_false_pattern(clause):
        # returns list of (qubit, need_x_wrap) to detect all-false pattern
        specs = []
        for var, negated in clause:
            if negated:
                # literal false when x==1 -> control on 1 (no wrap)
                specs.append((x[var], False))
            else:
                # literal false when x==0 -> control on 0 (wrap with X)
                specs.append((x[var], True))
        return specs

    def compute_clause(clause, target):
        specs = clause_controls_false_pattern(clause)
        # wrap controls that need |0> activation
        for q, wrap in specs:
            if wrap:
                qc.x(q)
        ctrls = [q for q, _ in specs]
        qc.mcx(ctrls, target)   # target ^= (all literals false)
        for q, wrap in specs:
            if wrap:
                qc.x(q)
        qc.x(target)            # now target = clause satisfied (1)

    def uncompute_clause(clause, target):
        specs = clause_controls_false_pattern(clause)
        qc.x(target)
        for q, wrap in specs:
            if wrap:
                qc.x(q)
        ctrls = [q for q, _ in specs]
        qc.mcx(ctrls, target)
        for q, wrap in specs:
            if wrap:
                qc.x(q)

    # compute all clause ancillas
    for clause, anc in zip(clauses, cl):
        compute_clause(clause, anc)

    # AND of all clause ancillas -> phase via multi-controlled Z on out
    qc.mcx(cl, out)
    qc.z(out)
    qc.mcx(cl, out)

    # uncompute clause ancillas (reverse order)
    for clause, anc in reversed(list(zip(clauses, cl))):
        uncompute_clause(clause, anc)
