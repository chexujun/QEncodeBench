from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # Clauses as lists of (variable_index, is_positive_literal)
    clauses = [
        [(0, True), (1, False), (4, False)],
        [(0, False), (1, False), (4, True)],
        [(0, False), (2, True), (3, False)],
        [(0, False), (3, False), (4, True)],
        [(2, False), (3, True), (4, True)],
        [(1, False), (3, True), (4, True)],
    ]
    n_clauses = len(clauses)
    clause_anc = ancilla_qubits[:n_clauses]   # one ancilla per clause
    out_anc = ancilla_qubits[n_clauses]       # final AND ancilla

    def compute():
        for c, lits in enumerate(clauses):
            a = clause_anc[c]
            # clause = OR of literals; ancilla should be 1 iff clause satisfied.
            # Use De Morgan: clause false iff all literals false.
            # A literal (i, pos) is TRUE iff qubit i == pos.
            # Set up controls so that ancilla flips to 1 unless all literals false.
            # Strategy: flip qubits so that "literal false" corresponds to control=1,
            # then MCX sets ancilla=1 when NOT all-false... simpler: compute clause-false
            # into ancilla, then X to get clause-true.
            # For each literal, it is FALSE when qubit i == (not pos).
            # Make control=|1> represent literal-false: apply X to qubit i if pos is True.
            ctrls = []
            for (i, pos) in lits:
                if pos:
                    qc.x(x[i])   # now qubit==1 means original 0 == literal false
                ctrls.append(x[i])
            qc.mcx(ctrls, a)     # a = 1 iff all literals false (clause unsatisfied)
            qc.x(a)              # a = 1 iff clause satisfied
            for (i, pos) in lits:
                if pos:
                    qc.x(x[i])   # restore

    def uncompute():
        for c in reversed(range(n_clauses)):
            lits = clauses[c]
            a = clause_anc[c]
            ctrls = []
            for (i, pos) in lits:
                if pos:
                    qc.x(x[i])
                ctrls.append(x[i])
            qc.x(a)
            qc.mcx(ctrls, a)
            for (i, pos) in lits:
                if pos:
                    qc.x(x[i])

    compute()
    # Now all clause ancillas are 1 iff their clause is satisfied.
    # Formula satisfied iff AND of all clause ancillas.
    qc.mcx(clause_anc, out_anc)   # out_anc = 1 iff all clauses satisfied
    qc.z(out_anc)                 # phase -1 on satisfying assignments
    qc.mcx(clause_anc, out_anc)   # uncompute out_anc
    uncompute()
