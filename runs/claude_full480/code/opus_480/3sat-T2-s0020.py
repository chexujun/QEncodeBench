from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4, x5 = [problem_qubits[i] for i in range(6)]

    # Clauses as (qubit, negated?) literal lists. Clause is satisfied unless
    # ALL literals are false. We compute an ancilla = 1 iff clause is VIOLATED
    # (all literals false), i.e. AND of the negation of each literal's truth.
    # A literal (q, neg=False)=x_q is true when q=1; violated needs q=0.
    # A literal (q, neg=True)=NOT x_q is true when q=0; violated needs q=1.
    clauses = [
        [(x1, True), (x4, True), (x5, False)],   # NOT x1 OR NOT x4 OR x5
        [(x0, False), (x1, False), (x4, True)],  # x0 OR x1 OR NOT x4
        [(x0, False), (x1, False), (x5, True)],  # x0 OR x1 OR NOT x5
        [(x1, False), (x3, False), (x5, True)],  # x1 OR x3 OR NOT x5
        [(x0, True), (x3, True), (x5, True)],    # NOT x0 OR NOT x3 OR NOT x5
    ]

    clause_ancillas = ancilla_qubits[:5]
    final_ancilla = ancilla_qubits[5]

    def clause_violated_controls(clause):
        # Returns (ctrl_qubits, x_flips): control qubits and which need X-flip
        # so that ctrl==1 corresponds to the literal being FALSE.
        ctrls = []
        flips = []
        for (q, neg) in clause:
            ctrls.append(q)
            # literal false when: (neg False -> q==0) needs flip; (neg True -> q==1) no flip
            if not neg:
                flips.append(q)  # need q==0 -> flip so control sees 1
        return ctrls, flips

    def compute_clause(clause, target):
        ctrls, flips = clause_violated_controls(clause)
        for q in flips:
            qc.x(q)
        qc.mcx(ctrls, target)  # target ^= 1 iff all literals false (clause violated)
        for q in flips:
            qc.x(q)

    # Compute per-clause "violated" flags
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # Formula satisfied iff NO clause is violated: all clause_ancillas == 0.
    # Flip clause ancillas so 1 means "satisfied", then AND into final_ancilla.
    for anc in clause_ancillas:
        qc.x(anc)
    qc.mcx(clause_ancillas, final_ancilla)  # final = 1 iff all clauses satisfied
    for anc in clause_ancillas:
        qc.x(anc)

    # Apply phase
    qc.z(final_ancilla)

    # Uncompute final_ancilla
    for anc in clause_ancillas:
        qc.x(anc)
    qc.mcx(clause_ancillas, final_ancilla)
    for anc in clause_ancillas:
        qc.x(anc)

    # Uncompute per-clause flags (mirror)
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)
