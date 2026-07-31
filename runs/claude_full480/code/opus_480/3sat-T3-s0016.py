from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    clause_anc = ancilla_qubits[:11]
    out = ancilla_qubits[11]

    # Each clause: list of (var_index, negated?) ; negated=True means literal is NOT x_i
    clauses = [
        [(2, True), (5, False), (6, True)],
        [(0, True), (1, True), (6, False)],
        [(0, False), (2, False), (4, False)],
        [(0, False), (3, False), (6, False)],
        [(2, False), (4, False), (5, True)],
        [(3, False), (5, True), (6, False)],
        [(2, True), (5, True), (6, False)],
        [(4, False), (5, False), (6, False)],
        [(2, False), (3, True), (5, False)],
        [(0, False), (4, True), (5, False)],
        [(0, True), (1, True), (2, True)],
    ]

    def compute_clauses():
        # For clause (l0 OR l1 OR l2): clause is false iff all literals false.
        # A literal x_i (negated=False) is false when x_i=0; negated=True is false when x_i=1.
        # Set anc=1 when clause satisfied: anc = OR of literals.
        # Trick: flip control qubits so that "all controls=1 means all literals FALSE",
        # then mcx sets anc to (all literals false); complement anc to get satisfied.
        for c_idx, clause in enumerate(clauses):
            a = clause_anc[c_idx]
            ctrls = []
            flips = []
            for (vi, neg) in clause:
                q = x[vi]
                # literal is FALSE when: (neg=False -> x=0), (neg=True -> x=1)
                # we want control active (=1) when literal is false.
                if not neg:
                    # false when x=0 -> need to flip x so control=1 at x=0
                    qc.x(q)
                    flips.append(q)
                # neg=True: false when x=1 -> control already 1, no flip
                ctrls.append(q)
            qc.mcx(ctrls, a)   # a=1 iff all literals false (clause unsatisfied)
            qc.x(a)            # a=1 iff clause satisfied
            for q in flips:
                qc.x(q)

    def uncompute_clauses():
        for c_idx in reversed(range(len(clauses))):
            clause = clauses[c_idx]
            a = clause_anc[c_idx]
            ctrls = []
            flips = []
            for (vi, neg) in clause:
                q = x[vi]
                if not neg:
                    qc.x(q)
                    flips.append(q)
                ctrls.append(q)
            qc.x(a)
            qc.mcx(ctrls, a)
            for q in flips:
                qc.x(q)

    compute_clauses()
    # out = AND of all clause ancillas; phase flip when all satisfied
    qc.h(out)
    qc.mcx(clause_anc, out)
    qc.h(out)
    qc.mcx(clause_anc, out)  # uncompute out back to |0>
    qc.h(out)                # wait: need proper uncompute
    qc.h(out)
    uncompute_clauses()
