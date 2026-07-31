from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # clause list: each clause is list of (var_index, is_negated)
    clauses = [
        [(0, True), (2, True), (4, True)],
        [(4, False), (6, False), (7, False)],
        [(0, False), (2, False), (6, False)],
        [(0, True), (6, True), (7, True)],
        [(1, True), (5, False), (7, False)],
        [(0, True), (4, False), (7, False)],
        [(1, True), (3, True), (7, True)],
        [(1, False), (3, False), (4, False)],
        [(2, True), (6, False), (7, True)],
        [(2, True), (3, True), (4, True)],
    ]
    clause_ancillas = ancilla_qubits[:len(clauses)]   # 10 ancillas, one per clause
    final_ancilla = ancilla_qubits[len(clauses)]      # 11th ancilla for the AND phase

    def compute_clauses():
        for cl, anc in zip(clauses, clause_ancillas):
            controls = []
            for (vi, neg) in cl:
                q = x[vi]
                # clause is (l0 OR l1 OR l2). It is FALSE only when every literal is false.
                # literal (var, negated=False) false when var=0; (var, negated=True) false when var=1.
                # We want ancilla = clause value. Compute NOT(all literals false).
                # A literal is false when: var==0 (positive) or var==1 (negated).
                # Flip so that "literal false" corresponds to control==1.
                if not neg:
                    qc.x(q)   # now q==1 means literal false
                controls.append(q)
            # ancilla starts |0>; set to 1 iff all literals false
            qc.mcx(controls, anc)
            # ancilla now = 1 iff clause UNSATISFIED; flip to get clause value
            qc.x(anc)
            # restore the positive-literal qubits
            for (vi, neg) in cl:
                if not neg:
                    qc.x(x[vi])

    def uncompute_clauses():
        for cl, anc in reversed(list(zip(clauses, clause_ancillas))):
            controls = []
            for (vi, neg) in cl:
                q = x[vi]
                if not neg:
                    qc.x(q)
                controls.append(q)
            qc.x(anc)
            qc.mcx(controls, anc)
            for (vi, neg) in cl:
                if not neg:
                    qc.x(x[vi])

    # compute all clause ancillas (each = clause truth value)
    compute_clauses()
    # phase -1 iff all clause ancillas are 1
    qc.h(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)
    qc.h(final_ancilla)
    # uncompute
    uncompute_clauses()
