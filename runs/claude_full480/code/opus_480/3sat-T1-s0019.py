from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[0:5]
    out = ancilla_qubits[5]

    # Clause definitions: (qubit, negated?) literals.
    # A clause is TRUE if any literal is satisfied. We compute clause-satisfaction
    # into ancilla c[k]: c[k]=1 iff clause k is satisfied.
    # clause OR of literals l = (var if not negated else NOT var).
    # Trick: clause is FALSE iff all literals false. Set c[k]=1, then use the
    # fact: compute NOT(clause) via controls, but easier: compute using De Morgan.
    clauses = [
        [(x1, True), (x2, False), (x3, False)],   # NOT x1 OR x2 OR x3
        [(x0, True), (x1, True), (x3, True)],     # NOT x0 OR NOT x1 OR NOT x3
        [(x0, True), (x1, False), (x2, True)],    # NOT x0 OR x1 OR NOT x2
        [(x1, True), (x2, False), (x3, True)],    # NOT x1 OR x2 OR NOT x3
        [(x0, True), (x2, True), (x3, False)],    # NOT x0 OR NOT x2 OR x3
    ]

    def prep(clause):
        # Flip qubits so that "literal satisfied" == qubit is |1>.
        # Literal (v, negated): satisfied when v == (0 if negated else 1).
        # We want control-on-|1> to mean satisfied, so for a literal satisfied
        # when v==1 (not negated) leave as is; when negated leave as is but the
        # MCX-all-zero approach needs different handling.
        # Instead: clause FALSE iff every literal FALSE.
        # literal FALSE means: not negated -> v==0 ; negated -> v==1.
        # We map each literal's "FALSE" condition to control-on-|1>:
        #   not negated: literal false when v==0 -> X then control on |1>
        #   negated:     literal false when v==1 -> control on |1> directly
        for v, negated in clause:
            if not negated:
                qc.x(v)

    def unprep(clause):
        for v, negated in clause:
            if not negated:
                qc.x(v)

    # For each clause: c[k] should become 1 when clause satisfied.
    # After prep, "all literal-vars == 1" means clause is FALSE.
    # So MCX(all vars) -> tmp sets tmp=1 iff clause false; we want c=NOT tmp.
    # Set c[k]=1, then MCX(all vars)->c[k] flips it to 0 iff clause false.
    for k, clause in enumerate(clauses):
        vs = [v for v, _ in clause]
        qc.x(c[k])
        prep(clause)
        qc.mcx(vs, c[k])
        unprep(clause)

    # Formula satisfied iff all c[k]==1.
    qc.mcx(c, out)
    qc.z(out)
    qc.mcx(c, out)

    # Uncompute clause ancillas (mirror).
    for k, clause in enumerate(reversed(clauses)):
        idx = len(clauses) - 1 - k
        vs = [v for v, _ in clause]
        prep(clause)
        qc.mcx(vs, c[idx])
        unprep(clause)
        qc.x(c[idx])
