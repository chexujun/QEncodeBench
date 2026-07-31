from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    # Each clause -> ancilla holds NOT(clause) = AND of negated literals.
    # clause satisfied  <=>  ancilla == 0.
    # We want phase -1 iff ALL clauses satisfied <=> all clause-ancillas == 0.
    # clauses: (lit variable index, is_negated_in_clause)
    clauses = [
        [(2, True),  (3, False), (5, False)],   # NOT x2 OR x3 OR x5
        [(2, False), (4, False), (5, False)],   # x2 OR x4 OR x5
        [(1, True),  (3, False), (5, True)],    # NOT x1 OR x3 OR NOT x5
        [(1, True),  (4, True),  (5, False)],   # NOT x1 OR NOT x4 OR x5
        [(0, False), (2, True),  (3, True)],    # x0 OR NOT x2 OR NOT x3
    ]

    def literal_true_controls(clause):
        # For clause ancilla to become 1 (clause FALSE), every literal must be false.
        # literal (v, neg): literal value = (NOT x_v) if neg else x_v.
        # literal false  <=> for neg=False: x_v == 0 ; for neg=True: x_v == 1.
        # We want ancilla = AND over literals of (literal false).
        # Control on x_v being at the "literal-false" value:
        #   neg=False -> need x_v == 0 -> control on |0> (apply X around, or use anti-control via X)
        #   neg=True  -> need x_v == 1 -> normal control
        return clause

    def compute(clause, target):
        # Set target = AND_lit (literal is false)
        flips = []
        controls = []
        for (v, neg) in clause:
            if not neg:
                # need x_v == 0 as the "true" control -> X-conjugate
                qc.x(p[v])
                flips.append(v)
            controls.append(p[v])
        qc.mcx(controls, target)
        for v in flips:
            qc.x(p[v])

    def uncompute(clause, target):
        flips = []
        controls = []
        for (v, neg) in clause:
            if not neg:
                qc.x(p[v])
                flips.append(v)
            controls.append(p[v])
        qc.mcx(controls, target)
        for v in flips:
            qc.x(p[v])

    n = len(clauses)
    # compute all clause-negation ancillas
    for i, clause in enumerate(clauses):
        compute(clause, anc[i])

    # Now clause i satisfied <=> anc[i] == 0. Formula satisfied <=> all anc == 0.
    # Phase -1 iff all anc == 0: conjugate with X on all clause ancillas, then
    # multi-controlled Z on them.
    for i in range(n):
        qc.x(anc[i])
    # multi-controlled Z: controls = anc[0..n-2], target anc[n-1] with H-conjugation
    ctrl = [anc[i] for i in range(n - 1)]
    tgt = anc[n - 1]
    qc.h(tgt)
    qc.mcx(ctrl, tgt)
    qc.h(tgt)
    for i in range(n):
        qc.x(anc[i])

    # uncompute clause ancillas (mirror)
    for i in reversed(range(n)):
        uncompute(clauses[i], anc[i])
