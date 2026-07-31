from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    a = ancilla_qubits

    # Clause literal specs: (qubit_index_in_x, negated?)
    # A clause (l0 OR l1 OR l2) is satisfied unless all literals are false.
    # Literal true when: variable==1 for positive, variable==0 for negated.
    # We compute clause_ancilla = clause_value (1 if satisfied).
    clauses = [
        [(1, True), (2, True), (3, False)],   # (NOT x1 OR NOT x2 OR x3)
        [(0, True), (1, True), (3, True)],    # (NOT x0 OR NOT x1 OR NOT x3)
        [(1, True), (2, False), (3, False)],  # (NOT x1 OR x2 OR x3)
        [(0, True), (1, False), (2, True)],   # (NOT x0 OR x1 OR NOT x2)
        [(1, False), (2, False), (3, True)],  # (x1 OR x2 OR NOT x3)
        [(0, False), (1, False), (3, False)], # (x0 OR x1 OR x3)
    ]

    clause_anc = a[0:6]  # one ancilla per clause
    final_anc = a[6]

    def compute_clauses():
        for ci, clause in enumerate(clauses):
            ctrls = [x[idx] for (idx, neg) in clause]
            # For an OR clause, satisfied = NOT(all literals false).
            # Literal false means: for positive literal var==0, for negated literal var==1.
            # Flip controls so that "all false" maps to all-ones on controls.
            # Positive literal false when var==0 -> apply X so control high when var==0.
            # Negated literal false when var==1 -> control high directly.
            for (idx, neg) in clause:
                if not neg:
                    qc.x(x[idx])  # now high == literal false
                # if neg: literal false when var==1, already high
            # clause_anc initially 0. Set to 1 (satisfied) by default, then
            # if all controls high (all literals false) flip back to 0.
            qc.x(clause_anc[ci])
            qc.mcx(ctrls, clause_anc[ci])
            # undo control flips
            for (idx, neg) in clause:
                if not neg:
                    qc.x(x[idx])

    compute_clauses()
    # Phase -1 iff all clause_anc == 1
    qc.h(final_anc)
    qc.x(final_anc)
    qc.mcx(clause_anc, final_anc)
    qc.x(final_anc)
    qc.h(final_anc)
    # Uncompute clauses (mirror)
    compute_clauses()
