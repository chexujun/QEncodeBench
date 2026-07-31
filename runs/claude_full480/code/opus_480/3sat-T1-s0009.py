from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]]
    out = ancilla_qubits[4]

    # Clause literals: (var_index, negated?) for the 4 clauses.
    # A clause is satisfied (=1) unless ALL its literals are false.
    # We compute clause-satisfied into c[k], then AND all four onto `out`.
    clauses = [
        [(0, True),  (1, False), (2, True)],   # (~x0 | x1 | ~x2)
        [(0, True),  (1, False), (2, False)],  # (~x0 | x1 |  x2)
        [(0, False), (1, True),  (2, False)],  # ( x0 | ~x1 | x2)
        [(0, True),  (1, True),  (2, False)],  # (~x0 | ~x1 | x2)
    ]

    def set_false_pattern(clause):
        # Flip so that the unique all-false assignment maps to all-ones.
        # Literal is false when: positive var == 0, or negated var == 1.
        # We want the qubit to be 1 exactly when the literal is false.
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])  # positive literal false when var==0 -> make 1

    # Compute each clause-satisfied bit into c[k].
    for k, clause in enumerate(clauses):
        qs = [problem_qubits[v] for (v, neg) in clause]
        # Turn each literal-false condition into a "1".
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])
        # c[k] = AND(all literals false)
        qc.mcx(qs, c[k])
        # c[k] currently = 1 iff clause UNsatisfied; flip to get satisfied.
        qc.x(c[k])
        # Undo the temporary X's on problem qubits.
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])

    # out = AND of all clause-satisfied bits
    qc.mcx(c, out)
    qc.z(out)
    qc.mcx(c, out)

    # Uncompute clause bits (mirror).
    for k, clause in enumerate(clauses):
        qs = [problem_qubits[v] for (v, neg) in clause]
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])
        qc.x(c[k])
        qc.mcx(qs, c[k])
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])
