from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Clause definitions: (qubit, is_negated) literals.
    # A clause is satisfied unless ALL its literals are false.
    # Literal true when: (not negated and qubit=1) or (negated and qubit=0).
    clauses = [
        [(x0, True),  (x1, False), (x2, False)],  # (NOT x0 OR x1 OR x2)
        [(x0, False), (x1, True),  (x2, False)],  # (x0 OR NOT x1 OR x2)
        [(x0, False), (x1, False), (x2, False)],  # (x0 OR x1 OR x2)
        [(x0, True),  (x1, False), (x2, True)],   # (NOT x0 OR x1 OR NOT x2)
        [(x0, False), (x1, False), (x2, True)],   # (x0 OR x1 OR NOT x2)
    ]

    def compute_clauses():
        for idx, clause in enumerate(clauses):
            # Flip qubits so that "all literals false" == "all controls 1".
            # A literal is false when: (not negated and q=0) -> need X to make 1;
            #                          (negated and q=1) -> need X to make 1.
            # So apply X to a qubit when the literal is NON-negated (false at 0),
            # and apply X when negated? Let's define: control should be 1 exactly
            # when the literal is FALSE.
            # literal false: non-negated -> q=0 ; negated -> q=1.
            # To turn "literal false" into control=1: non-negated needs X (0->1);
            # negated needs no X (already 1 when false).
            flips = [q for (q, neg) in clause if not neg]
            for q in flips:
                qc.x(q)
            ctrls = [q for (q, neg) in clause]
            # clause ancilla = 1 iff all literals false (clause violated)
            qc.mcx(ctrls, c[idx])
            for q in flips:
                qc.x(q)

    # Compute violation flags for all clauses.
    compute_clauses()

    # Formula satisfied iff NO clause is violated, i.e. all c[idx] == 0.
    # Flip clause flags so that "all satisfied" -> all controls 1.
    for ci in c:
        qc.x(ci)
    qc.mcx(c, out)          # out = 1 iff formula satisfied
    for ci in c:
        qc.x(ci)

    # Phase.
    qc.z(out)

    # Uncompute out.
    for ci in c:
        qc.x(ci)
    qc.mcx(c, out)
    for ci in c:
        qc.x(ci)

    # Uncompute clause flags (mirror).
    compute_clauses()
