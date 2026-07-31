from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c0, c1, c2, c3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    out = ancilla_qubits[4]

    # Clause literals: 1 means literal true. Clause satisfied if any literal true.
    # We compute clause_ok into an ancilla using De Morgan:
    # clause = OR of literals = NOT(AND of negated literals).
    # For each clause, flip the problem qubits so that "all negated-literals true"
    # corresponds to all-controls-1, use mcx to set ancilla, then it's the UNSAT case.
    # We set ancilla = 1 when clause is UNSAT (all literals false), then the
    # AND of (NOT unsat) is what we want. Easier: compute clause_ok = 1 when satisfied.

    clauses = [
        # (var, negated?) ; literal true when qubit == (0 if negated else 1)
        [(x0, True), (x1, False), (x2, True)],   # (NOT x0 OR x1 OR NOT x2)
        [(x0, True), (x1, True), (x2, False)],   # (NOT x0 OR NOT x1 OR x2)
        [(x0, False), (x1, False), (x2, False)], # (x0 OR x1 OR x2)
        [(x0, True), (x1, False), (x2, False)],  # (NOT x0 OR x1 OR x2)
    ]
    clause_anc = [c0, c1, c2, c3]

    def compute():
        for (qs, canc) in zip(clauses, clause_anc):
            # literal true when qubit == target. Clause UNSAT when all literals false,
            # i.e. each qubit == (opposite of its literal-true value).
            # literal-true value = 0 if negated else 1. false value = opposite.
            # For mcx to fire on "all false", flip qubits whose false-value is 0 so control=1.
            flips = []
            for (q, neg) in qs:
                true_val = 0 if neg else 1
                false_val = 1 - true_val
                # want control active (=1) when qubit == false_val
                if false_val == 0:
                    qc.x(q)
                    flips.append(q)
            controls = [q for (q, neg) in qs]
            qc.mcx(controls, canc)   # canc = 1 iff clause UNSAT
            qc.x(canc)               # canc = 1 iff clause SAT
            for q in flips:
                qc.x(q)

    compute()
    # out = AND of all clause_anc (all clauses satisfied)
    qc.mcx(clause_anc, out)
    qc.z(out)
    qc.mcx(clause_anc, out)
    # uncompute clause ancillas (mirror)
    for (qs, canc) in reversed(list(zip(clauses, clause_anc))):
        flips = []
        for (q, neg) in qs:
            true_val = 0 if neg else 1
            false_val = 1 - true_val
            if false_val == 0:
                qc.x(q)
                flips.append(q)
        qc.x(canc)
        controls = [q for (q, neg) in qs]
        qc.mcx(controls, canc)
        for q in flips:
            qc.x(q)
