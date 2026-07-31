from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits

    clauses = [
        [(1, False), (2, False), (3, True)],
        [(2, True), (3, True), (4, False)],
        [(1, True), (2, True), (5, False)],
        [(1, False), (3, True), (5, True)],
        [(0, False), (3, True), (5, False)],
        [(0, False), (1, True), (2, True)],
        [(0, False), (1, True), (3, True)],
        [(2, True), (3, True), (5, False)],
        [(3, True), (4, False), (5, True)],
        [(0, False), (2, True), (5, True)],
        [(0, True), (2, False), (3, True)],
        [(0, False), (1, True), (5, False)],
        [(0, False), (1, False), (4, True)],
    ]

    clause_anc = ancilla_qubits[:len(clauses)]
    final_anc = ancilla_qubits[len(clauses)]

    def compute():
        for c, a in zip(clauses, clause_anc):
            # clause literal is (var, positive). clause true iff any literal true.
            # NOT-clause (clause false) iff all literals false.
            # We set ancilla a = clause value.
            # Compute all-literals-false into a via: flip inputs so literal-true -> 1,
            # then a = NOT (AND of negated) ... use De Morgan.
            controls = []
            flips = []
            for var, positive in c:
                q = x[var]
                # literal is true when qubit == (1 if positive else 0)
                # For an OR clause: clause = OR of literals.
                # clause false <=> every literal false <=> for each, qubit == (0 if positive else 1)
                # Make a control that is 1 when literal is false:
                # literal false when qubit == (0 if positive else 1)
                if positive:
                    # false when qubit==0 -> need X before using as control
                    flips.append(q)
                controls.append(q)
            # apply X to flips so that "literal false" maps to control=1
            for q in flips:
                qc.x(q)
            # now literal-false <=> control qubit == 1 for all
            # a should = clause value = NOT(all controls ==1)
            # set a = AND(controls) then we will interpret; instead set a = clause = 1 - AND
            qc.mcx(controls, a)   # a ^= AND(controls) ; a starts 0 -> a = all-false
            qc.x(a)               # a = NOT(all-false) = clause value
            # undo flips
            for q in flips:
                qc.x(q)

    compute()
    # final_anc = AND of all clause values
    qc.mcx(clause_anc, final_anc)
    qc.z(final_anc)
    qc.mcx(clause_anc, final_anc)
    # uncompute clauses (mirror)
    for c, a in zip(reversed(clauses), reversed(clause_anc)):
        flips = [x[var] for var, positive in c if positive]
        controls = [x[var] for var, positive in c]
        for q in flips:
            qc.x(q)
        qc.x(a)
        qc.mcx(controls, a)
        for q in flips:
            qc.x(q)
