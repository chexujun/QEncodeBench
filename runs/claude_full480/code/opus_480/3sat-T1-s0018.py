from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    clause_anc = ancilla_qubits[:5]
    phase_anc = ancilla_qubits[5]

    # Each clause: (l0 OR l1 OR l2). Clause ancilla = 1 iff clause satisfied.
    # Compute via De Morgan: clause is FALSE iff all literals false.
    # Set ancilla to NOT(all-literals-false).
    # literal NOT xi is true when xi==0; literal xi true when xi==1.
    # clauses as (qubit, negated?) triples; negated=True means literal is NOT x.
    clauses = [
        [(x0, True),  (x1, False), (x2, True)],   # (NOT x0 OR x1 OR NOT x2)
        [(x0, True),  (x1, True),  (x2, True)],   # (NOT x0 OR NOT x1 OR NOT x2)
        [(x0, True),  (x1, True),  (x2, False)],  # (NOT x0 OR NOT x1 OR x2)
        [(x0, False), (x1, True),  (x2, False)],  # (x0 OR NOT x1 OR x2)
        [(x0, False), (x1, False), (x2, False)],  # (x0 OR x1 OR x2)
    ]

    def compute_clause(clause, anc):
        # Flip qubits so that "literal false" corresponds to |1> being needed,
        # then the clause-false condition is all three == 0 after mapping.
        # We want anc=1 iff clause satisfied. Clause false iff every literal false.
        # A literal xi (negated=False) is false when xi==0.
        # A literal NOT xi (negated=True) is false when xi==1.
        # Map each qubit so that value 1 == literal-false: for negated literal, keep xi;
        # for non-negated literal, apply X so that xi==0 -> 1.
        for (q, neg) in clause:
            if not neg:
                qc.x(q)
        # Now literal-false <=> qubit==1 for all. Clause false <=> all three qubits==1.
        # ccx sets anc ^= (all three ==1); anc starts 0 -> anc = clause-false.
        qc.ccx(clause[0][0], clause[1][0], anc)  # partial
        # need triple control; use mcx
        # revert partial: instead do proper mcx below

    # Simpler: do compute + uncompute using X-mapping and mcx for all-ones detection,
    # then X the ancilla to get clause-satisfied.
    def apply_map(clause):
        for (q, neg) in clause:
            if not neg:
                qc.x(q)

    def compute(clause, anc):
        apply_map(clause)
        qc.mcx([clause[0][0], clause[1][0], clause[2][0]], anc)  # anc = all-false
        qc.x(anc)  # anc = clause satisfied
        apply_map(clause)  # undo X on problem qubits

    def uncompute(clause, anc):
        apply_map(clause)
        qc.x(anc)
        qc.mcx([clause[0][0], clause[1][0], clause[2][0]], anc)
        apply_map(clause)

    for clause, anc in zip(clauses, clause_anc):
        compute(clause, anc)

    # phase_anc = AND of all clause ancillas; phase it.
    qc.mcx(clause_anc, phase_anc)
    qc.z(phase_anc)
    qc.mcx(clause_anc, phase_anc)

    for clause, anc in zip(clauses, clause_anc):
        uncompute(clause, anc)
