from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Clause definitions: each clause is a list of (qubit, negated) literals.
    # A clause ancilla will hold 1 iff the clause is SATISFIED.
    # We compute (clause satisfied) = NOT(all literals false).
    # Literal l is true when qubit == (0 if negated else 1).
    clauses = [
        [(x1, False), (x2, True), (x3, True)],   # (x1 OR NOT x2 OR NOT x3)
        [(x1, True), (x2, False), (x3, False)],  # (NOT x1 OR x2 OR x3)
        [(x0, True), (x2, False), (x3, False)],  # (NOT x0 OR x2 OR x3)
        [(x0, False), (x1, False), (x3, True)],  # (x0 OR x1 OR NOT x3)
        [(x0, True), (x2, False), (x3, True)],   # (NOT x0 OR x2 OR NOT x3)
    ]

    def flip_to_falsify(clause):
        # For each literal, arrange that qubit==1 means "literal is FALSE".
        # Literal true when qubit==(0 if negated else 1). So literal false when
        # qubit==(1 if negated else 0). We want a marker=1 meaning literal false.
        # Apply X so that the qubit reads 1 exactly when the literal is false:
        #   negated literal: false when qubit==1 -> no X
        #   positive literal: false when qubit==0 -> X
        for (q, negated) in clause:
            if not negated:
                qc.x(q)

    def compute_clause(clause, anc):
        # After flip_to_falsify, all-1 on the clause qubits means clause unsatisfied.
        qs = [q for (q, _) in clause]
        # anc initially 0. Set anc=1 iff NOT all-ones -> compute all-ones into anc then flip.
        qc.mcx(qs, anc)   # anc = AND(all literals false) = clause unsatisfied
        qc.x(anc)         # anc = clause satisfied

    # Compute all clause ancillas
    for i, clause in enumerate(clauses):
        flip_to_falsify(clause)
        compute_clause(clause, c[i])
        flip_to_falsify(clause)  # restore problem qubits

    # Formula satisfied iff all clause ancillas are 1. Apply phase via multi-controlled Z.
    qc.h(out)
    qc.mcx(c, out)
    qc.h(out)

    # Uncompute clause ancillas (mirror)
    for i, clause in reversed(list(enumerate(clauses))):
        flip_to_falsify(clause)
        qc.x(c[i])
        qc.mcx([q for (q, _) in clause], c[i])
        flip_to_falsify(clause)
