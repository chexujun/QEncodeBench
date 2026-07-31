from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:8]   # one ancilla per clause
    out = ancilla_qubits[8]   # final AND ancilla

    # Clause definitions: list of (var_index, is_negated) literals.
    # Clause is satisfied unless ALL literals are false.
    clauses = [
        [(1, False), (3, True), (6, False)],
        [(3, True), (5, False), (6, True)],
        [(0, False), (3, True), (4, False)],
        [(1, False), (3, True), (5, False)],
        [(0, True), (3, False), (7, False)],
        [(0, False), (2, False), (3, False)],
        [(3, False), (4, True), (6, False)],
        [(2, True), (5, False), (7, True)],
    ]

    def compute_clause(clause, anc):
        # anc must start in |0>. Set anc = clause_value (1 if satisfied).
        # A literal (i, neg): literal true iff qubit==1 (neg False) or qubit==0 (neg True).
        # Clause false iff all literals false. For literal to be FALSE:
        #   neg False -> qubit==0 ; neg True -> qubit==1.
        # We want anc=1 when clause satisfied. Compute via:
        #   Flip control qubits so that "all literals false" corresponds to all controls=1,
        #   set anc via X then multi-controlled X that turns it off.
        ctrls = []
        for (i, neg) in clause:
            # literal false when: (neg False and qubit==0) or (neg True and qubit==1)
            # We want a control that is 1 exactly when literal is false.
            # If neg False: literal false at qubit==0 -> apply X to make control=1 at qubit==0.
            if not neg:
                qc.x(x[i])
            ctrls.append(x[i])
        # Now all ctrls==1 means all literals false means clause NOT satisfied.
        qc.x(anc)  # tentatively satisfied
        qc.mcx(ctrls, anc)  # if all literals false, unset -> clause=0
        # Restore flipped qubits
        for (i, neg) in clause:
            if not neg:
                qc.x(x[i])

    def uncompute_clause(clause, anc):
        # mirror of compute_clause (same self-inverse structure)
        ctrls = []
        for (i, neg) in clause:
            if not neg:
                qc.x(x[i])
            ctrls.append(x[i])
        qc.mcx(ctrls, anc)
        qc.x(anc)
        for (i, neg) in clause:
            if not neg:
                qc.x(x[i])

    # Compute all clause ancillas
    for c, anc in zip(clauses, cl):
        compute_clause(c, anc)

    # out = AND of all clause ancillas
    qc.mcx(cl, out)

    # phase
    qc.z(out)

    # uncompute out
    qc.mcx(cl, out)

    # uncompute clause ancillas (reverse order)
    for c, anc in zip(reversed(clauses), reversed(cl)):
        uncompute_clause(c, anc)
