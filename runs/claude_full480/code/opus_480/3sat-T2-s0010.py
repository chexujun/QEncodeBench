from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]   # one ancilla per clause
    out = ancilla_qubits[6]   # final AND target

    # Each clause: (l0 OR l1 OR l2). Compute clause-satisfied bit into an ancilla.
    # Clause literals: (qubit_index, negated?) where negated True means literal is NOT x_i.
    clauses = [
        [(2, True), (3, True), (5, True)],   # NOT x2 OR NOT x3 OR NOT x5
        [(0, True), (3, False), (5, False)], # NOT x0 OR x3 OR x5
        [(1, False), (4, False), (5, False)],# x1 OR x4 OR x5
        [(0, True), (1, True), (4, True)],   # NOT x0 OR NOT x1 OR NOT x4
        [(0, False), (1, False), (2, False)],# x0 OR x1 OR x2
        [(0, False), (1, True), (5, False)], # x0 OR NOT x1 OR x5
    ]

    def compute_clause(lits, target):
        # OR = NOT(AND of negated literals).
        # A literal l is TRUE when: positive literal -> qubit=1; negative literal -> qubit=0.
        # Clause is FALSE only when all literals FALSE.
        # literal FALSE: positive -> qubit=0 ; negative -> qubit=1.
        # Set up controls so that mcx fires (target flips) exactly when clause is FALSE.
        # For each literal, we want control active when literal is FALSE.
        # positive literal false when qubit=0 -> need X before/after so control on |1> reads |0>.
        # negative literal false when qubit=1 -> control directly on |1>.
        flips = []
        controls = []
        for (qi, neg) in lits:
            if neg:
                # literal false when qubit == 1 -> control on 1 directly
                controls.append(x[qi])
            else:
                # literal false when qubit == 0 -> flip so control-on-1 detects 0
                qc.x(x[qi])
                flips.append(x[qi])
                controls.append(x[qi])
        # target flips iff clause FALSE (all controls == 1)
        qc.mcx(controls, target)
        # target currently = 1 when clause FALSE. We want clause-satisfied = NOT that.
        qc.x(target)
        for q in flips:
            qc.x(q)

    def uncompute_clause(lits, target):
        flips = []
        controls = []
        for (qi, neg) in lits:
            if neg:
                controls.append(x[qi])
            else:
                qc.x(x[qi])
                flips.append(x[qi])
                controls.append(x[qi])
        qc.x(target)
        qc.mcx(controls, target)
        for q in flips:
            qc.x(q)

    # Compute all clause-satisfied bits.
    for c, target in zip(clauses, cl):
        compute_clause(c, target)

    # out = AND of all clause bits -> flips when formula satisfied.
    qc.mcx(cl, out)

    # Phase: -1 iff formula satisfied.
    qc.z(out)

    # Uncompute.
    qc.mcx(cl, out)
    for c, target in reversed(list(zip(clauses, cl))):
        uncompute_clause(c, target)
