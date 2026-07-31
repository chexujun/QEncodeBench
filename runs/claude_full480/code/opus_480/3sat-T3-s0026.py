import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    clause_anc = ancilla_qubits[:10]
    out = ancilla_qubits[10]

    # Each clause: list of (var_index, is_negated)
    clauses = [
        [(2, True), (4, True), (6, True)],
        [(4, False), (5, False), (6, True)],
        [(0, True), (1, False), (3, True)],
        [(0, True), (3, False), (4, True)],
        [(3, True), (5, False), (6, False)],
        [(1, True), (2, True), (6, False)],
        [(0, True), (3, False), (5, False)],
        [(0, False), (5, True), (6, True)],
        [(0, False), (3, True), (5, True)],
        [(0, False), (1, False), (2, True)],
    ]

    def clause_compute(ci):
        lits = clauses[ci]
        a = clause_anc[ci]
        ctrls = [x[v] for (v, neg) in lits]
        # For an OR clause, clause is FALSE iff every literal is false.
        # Literal (v, neg): literal true when qubit == (0 if neg else 1).
        # We compute clause_anc = OR of literals.
        # Set ancilla to 1 iff clause satisfied:
        # First flip controls so that "all-false" maps to all-ones control,
        # then MCX sets ancilla when clause is UNSAT, and X flips to SAT.
        for (v, neg) in lits:
            # literal false when: neg -> qubit==1 ; not neg -> qubit==0
            # We want control-active(=1) to mean literal false.
            if not neg:
                qc.x(x[v])   # now qubit==1 means original 0 => literal false
            # if neg, literal false when qubit==1 already (control active)
        qc.mcx(ctrls, a)     # a=1 iff all literals false (clause unsat)
        for (v, neg) in lits:
            if not neg:
                qc.x(x[v])
        qc.x(a)              # a=1 iff clause satisfied

    # Compute all clause ancillas
    for ci in range(len(clauses)):
        clause_compute(ci)

    # AND of all clause ancillas into phase
    qc.h(out)
    qc.mcx(clause_anc, out)
    qc.h(out)

    # Uncompute clause ancillas (mirror)
    for ci in reversed(range(len(clauses))):
        clause_compute(ci)
