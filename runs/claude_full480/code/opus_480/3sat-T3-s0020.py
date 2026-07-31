from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    # Variables x0..x7 on problem_qubits[0..7]
    x = problem_qubits
    # Clauses as list of literals (var_index, is_negated)
    clauses = [
        [(1, True), (3, True), (6, False)],
        [(1, False), (6, False), (7, True)],
        [(2, True), (5, False), (6, True)],
        [(2, True), (3, True), (7, True)],
        [(0, False), (1, False), (6, True)],
        [(0, True), (1, False), (3, False)],
        [(2, False), (3, True), (6, True)],
        [(1, False), (4, True), (6, True)],
        [(2, True), (6, True), (7, False)],
    ]

    n_clauses = len(clauses)
    clause_anc = ancilla_qubits[:n_clauses]  # 9 ancillas, one per clause
    out = ancilla_qubits[n_clauses]          # 10th ancilla holds the AND

    def compute():
        # For each clause, set clause ancilla = OR of literals.
        # Clause is FALSE iff all literals are false.
        # A literal (v, neg): literal true iff (qubit == 1) XOR neg... 
        # neg=True means literal is NOT x_v -> true when qubit==0.
        for c_idx, lits in enumerate(clauses):
            a = clause_anc[c_idx]
            controls = []
            # We want clause ancilla a = 1 iff clause satisfied.
            # Compute NOT(all literals false): set a=1 unless every literal false.
            # Flip qubits so that "literal false" corresponds to control value 1.
            # literal (v, neg): literal false when qubit == neg? 
            #   neg=False (positive literal x_v): false when qubit==0
            #   neg=True  (negative literal ~x_v): false when qubit==1
            for (v, neg) in lits:
                q = x[v]
                # want control-active (=1) when literal is FALSE
                if not neg:
                    # positive: false when qubit==0 -> X so 0->1
                    qc.x(q)
                # negative: false when qubit==1 -> already 1, no X
                controls.append(q)
            # If all three controls are 1 => clause false => a stays 0.
            # We want a=1 when clause satisfied => a = NOT(all controls 1).
            # Set a=1 first, then MCX flips it to 0 when all controls 1.
            qc.x(a)
            qc.mcx(controls, a)
            # undo the X flips on positive-literal qubits
            for (v, neg) in lits:
                if not neg:
                    qc.x(x[v])

    compute()
    # out = AND of all clause ancillas
    qc.mcx(clause_anc, out)
    qc.z(out)
    qc.mcx(clause_anc, out)
    # uncompute clause ancillas (mirror)
    for c_idx in reversed(range(n_clauses)):
        lits = clauses[c_idx]
        a = clause_anc[c_idx]
        controls = []
        for (v, neg) in lits:
            q = x[v]
            if not neg:
                qc.x(q)
            controls.append(q)
        qc.mcx(controls, a)
        qc.x(a)
        for (v, neg) in lits:
            if not neg:
                qc.x(x[v])
