from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[:4]
    out = ancilla_qubits[4]

    # Clause literals: (lit on x_i). A clause is satisfied unless ALL its
    # literals are false. We compute clause_ok into c[k] using the pattern:
    # a clause (l_a OR l_b OR l_c) is FALSE exactly for one assignment of
    # (x_a,x_b,x_c). We set c[k]=1 when clause is satisfied.
    # Implement: c[k] = NOT(all literals false). Use mcx onto c[k] after
    # setting the "all-false" detector, then X to invert.

    clauses = [
        [(x0, True),  (x1, False), (x2, True)],   # (NOT x0 OR x1 OR NOT x2)
        [(x0, True),  (x1, True),  (x2, True)],   # (NOT x0 OR NOT x1 OR NOT x2)
        [(x0, True),  (x1, False), (x2, False)],  # (NOT x0 OR x1 OR x2)
        [(x0, False), (x1, False), (x2, True)],   # (x0 OR x1 OR NOT x2)
    ]
    # For each literal, "negate" flag True means literal is (NOT x_i), so the
    # literal is false when x_i = 1 -> we need x_i control on |1>. The literal
    # is false when x_i equals `negate_value`. To detect all-literals-false we
    # want controls that fire when each x_i is at its clause-falsifying value.
    # For literal (NOT x_i): false when x_i=1 -> control on 1 (no X).
    # For literal (x_i):     false when x_i=0 -> control on 0 (apply X first).

    def compute_clause(lits, target):
        flips = []
        ctrls = []
        for (q, is_negated) in lits:
            if is_negated:
                # literal (NOT x): false when x=1 -> control on 1, no flip
                ctrls.append(q)
            else:
                # literal (x): false when x=0 -> flip to control on 1
                flips.append(q)
                ctrls.append(q)
        for q in flips:
            qc.x(q)
        qc.mcx(ctrls, target)  # target=1 iff all literals false (clause UNsat)
        for q in flips:
            qc.x(q)
        qc.x(target)           # target=1 iff clause satisfied

    def uncompute_clause(lits, target):
        qc.x(target)
        flips = []
        ctrls = []
        for (q, is_negated) in lits:
            if is_negated:
                ctrls.append(q)
            else:
                flips.append(q)
                ctrls.append(q)
        for q in flips:
            qc.x(q)
        qc.mcx(ctrls, target)
        for q in flips:
            qc.x(q)

    for k, lits in enumerate(clauses):
        compute_clause(lits, c[k])

    qc.h(out)
    qc.mcx(c, out)
    qc.h(out)

    for k in reversed(range(len(clauses))):
        uncompute_clause(clauses[k], c[k])
