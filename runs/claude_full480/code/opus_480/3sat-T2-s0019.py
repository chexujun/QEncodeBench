from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Clause 0: (x0 OR NOT x1 OR x2) -> false iff x0=0, x1=1, x2=0
    #   c0 = NOT(clause0) i.e. c0=1 when clause violated
    def clause_compute(target, lits):
        # lits: list of (qubit, negated_bool) where literal is qubit if not negated else NOT qubit
        # clause satisfied if any literal true; violated (c=1) if all literals false.
        # literal false means qubit == (1 if not negated else 0)... let's define:
        # literal (q, neg=False) true when q=1; false when q=0
        # literal (q, neg=True)  true when q=0; false when q=1
        # For target = AND of (literal false) we need each literal-false condition = 1.
        # literal false condition: q==0 for neg=False -> need X first; q==1 for neg=True -> as is.
        flips = []
        controls = []
        for (q, neg) in lits:
            if not neg:
                # literal false when q==0 -> control on q after X
                qc.x(q)
                flips.append(q)
            controls.append(q)
        qc.mcx(controls, target)
        for q in flips:
            qc.x(q)

    clauses = [
        [(x0, False), (x1, True), (x2, False)],
        [(x1, False), (x2, True), (x3, False)],
        [(x1, False), (x2, False), (x3, False)],
        [(x1, False), (x2, True), (x3, True)],
        [(x0, False), (x1, True), (x3, False)],
    ]

    # compute violation flags
    for i, cl in enumerate(clauses):
        clause_compute(c[i], cl)

    # formula satisfied iff all violation flags are 0.
    # out = 1 iff all c[i]==0. Compute by X on all c, mcx, then X back is uncompute of flags separately.
    for i in range(5):
        qc.x(c[i])
    qc.mcx(c, out)
    for i in range(5):
        qc.x(c[i])

    # phase
    qc.z(out)

    # uncompute out
    for i in range(5):
        qc.x(c[i])
    qc.mcx(c, out)
    for i in range(5):
        qc.x(c[i])

    # uncompute violation flags (mirror)
    for i in range(4, -1, -1):
        clause_compute(c[i], clauses[i])
