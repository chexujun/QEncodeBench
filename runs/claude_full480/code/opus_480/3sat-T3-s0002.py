import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    # 7 clause ancillas + 1 phase ancilla
    ca = ancilla_qubits[:7]

    # Each clause: (l0 OR l1 OR l2). A clause is FALSE iff all literals false.
    # We set clause ancilla = 1 iff clause is SATISFIED using De Morgan:
    #   flip each literal's control so that we detect the all-false pattern,
    #   set ancilla to NOT(all-false).
    # Represent each clause by (qubit, negated?) triples.
    clauses = [
        [(0, True),  (2, True),  (4, False)],   # ¬x0 ∨ ¬x2 ∨ x4
        [(2, False), (4, False), (5, True)],    # x2 ∨ x4 ∨ ¬x5
        [(1, False), (2, False), (4, True)],    # x1 ∨ x2 ∨ ¬x4
        [(1, False), (2, False), (5, True)],    # x1 ∨ x2 ∨ ¬x5
        [(0, True),  (1, True),  (4, True)],    # ¬x0 ∨ ¬x1 ∨ ¬x4
        [(0, False), (2, False), (4, False)],   # x0 ∨ x2 ∨ x4
        [(0, True),  (4, True),  (5, False)],   # ¬x0 ∨ ¬x4 ∨ x5
    ]

    def compute_clause(cl, target):
        # A literal is TRUE when: (not negated and qubit=1) or (negated and qubit=0).
        # Clause satisfied iff at least one literal TRUE.
        # Detect the all-literals-FALSE pattern with an MCX whose controls are 1
        # exactly when every literal is false, then invert target.
        # Literal false when: (not negated and qubit=0) or (negated and qubit=1).
        # Map each control qubit to be |1> in the all-false pattern:
        #   non-negated literal false at qubit=0  -> X before, X after
        #   negated literal false at qubit=1      -> use qubit directly
        ctrls = []
        for q, neg in cl:
            if not neg:
                qc.x(x[q])   # so control is 1 when qubit was 0 (literal false)
            ctrls.append(x[q])
        qc.mcx(ctrls, target)   # target ^= (all literals false)
        for q, neg in cl:
            if not neg:
                qc.x(x[q])
        qc.x(target)            # target = NOT(all false) = clause satisfied

    # Compute all clause ancillas
    for cl, t in zip(clauses, ca):
        compute_clause(cl, t)

    # Phase: -1 iff all clause ancillas are 1 (formula satisfied)
    qc.h(ca[-1])
    qc.mcx(ca[:-1], ca[-1])
    qc.h(ca[-1])

    # Uncompute all clause ancillas (mirror)
    for cl, t in zip(reversed(clauses), reversed(ca)):
        compute_clause(cl, t)
