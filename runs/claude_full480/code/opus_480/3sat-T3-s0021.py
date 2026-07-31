from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # 7 clause ancillas + 1 phase ancilla
    ca = ancilla_qubits[:7]
    pa = ancilla_qubits[7]

    # Each clause: (l_a OR l_b OR l_c). Compute clause-satisfied flag into ancilla.
    # A clause is satisfied unless all three literals are false.
    # We set ancilla = 1 when clause is SAT using: clause = NOT(all literals false).
    # For literal x_i (positive), "false" means qubit==0; for NOT x_i, "false" means qubit==1.
    # Strategy: flip qubits so that "literal false" corresponds to |1>, then the
    # all-false condition = all three control qubits ==1 -> use mcx to set ancilla,
    # then X on ancilla to get clause-SAT. Uncompute the flips.

    # clause spec: list of (qubit_index, negated?) ; literal false when:
    #   positive literal false <=> qubit==0  -> need X to map to 1
    #   negated  literal false <=> qubit==1  -> already 1, no X
    clauses = [
        [(2, False), (3, False), (4, False)],
        [(2, False), (4, False), (5, False)],
        [(0, True),  (1, False), (5, False)],
        [(0, False), (3, True),  (5, False)],
        [(0, True),  (3, True),  (4, True)],
        [(0, True),  (1, True),  (2, False)],
        [(0, True),  (3, False), (5, False)],
    ]

    def apply_flips(clause):
        # after flips, each control qubit == 1 iff its literal is FALSE
        for (qi, neg) in clause:
            if not neg:
                qc.x(x[qi])

    def compute_clause(clause, anc):
        apply_flips(clause)
        ctrls = [x[qi] for (qi, _) in clause]
        qc.mcx(ctrls, anc)   # anc = 1 iff all literals false (clause UNSAT)
        apply_flips(clause)  # undo flips
        qc.x(anc)            # anc = 1 iff clause SAT

    # compute all clause flags
    for c, anc in zip(clauses, ca):
        compute_clause(clauses[clauses.index(c)] if False else c, anc)

    # phase: -1 iff all clause flags == 1 (formula satisfied)
    qc.h(pa)
    qc.mcx(ca, pa)
    qc.h(pa)

    # uncompute clause flags (mirror)
    for c, anc in zip(reversed(clauses), reversed(ca)):
        qc.x(anc)
        apply_flips(c)
        ctrls = [x[qi] for (qi, _) in c]
        qc.mcx(ctrls, anc)
        apply_flips(c)
