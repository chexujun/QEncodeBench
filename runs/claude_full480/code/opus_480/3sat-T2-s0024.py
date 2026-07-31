import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c0, c1, c2, c3, out = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]

    # Clause definitions: (qubit, negated?) literals.
    # A clause ancilla will be set to 1 iff the clause is SATISFIED.
    # Clause = OR of literals; literal true when qubit == (0 if negated else 1).
    clauses = [
        (c0, [(x0, False), (x1, False), (x3, False)]),   # x0 OR x1 OR x3
        (c1, [(x0, True), (x1, False), (x2, True)]),     # ~x0 OR x1 OR ~x2
        (c2, [(x0, True), (x2, False), (x3, True)]),     # ~x0 OR x2 OR ~x3
        (c3, [(x1, True), (x2, True), (x3, False)]),     # ~x1 OR ~x2 OR x3
    ]

    def compute_clause(anc, lits):
        # Set anc = OR(literals). Use De Morgan: OR = NOT(AND of negated literals).
        # For each literal, the literal is FALSE when qubit == (1 if negated else 0).
        # We compute AND of (NOT literal) into anc via mcx over controls set so that
        # control is 1 exactly when the literal is false.
        ctrls = []
        flips = []
        for q, neg in lits:
            # literal false condition: qubit value == (1 if neg else 0)
            # want control active (=1) when literal is false.
            if neg:
                # negated literal x' ; literal true when q==0, false when q==1 -> control = q
                ctrls.append(q)
            else:
                # literal true when q==1, false when q==0 -> control = NOT q
                qc.x(q)
                flips.append(q)
                ctrls.append(q)
        # anc currently 0; mcx flips anc to 1 iff all literals false (AND of negated literals)
        qc.mcx(ctrls, anc)
        # anc = (all literals false). We want OR = NOT that.
        qc.x(anc)
        for q in flips:
            qc.x(q)

    def uncompute_clause(anc, lits):
        flips = []
        ctrls = []
        for q, neg in lits:
            if neg:
                ctrls.append(q)
            else:
                qc.x(q)
                flips.append(q)
                ctrls.append(q)
        qc.x(anc)
        qc.mcx(ctrls, anc)
        for q in flips:
            qc.x(q)

    # Compute all clause ancillas.
    for anc, lits in clauses:
        compute_clause(anc, lits)

    # out = AND of all clause ancillas -> phase via Z, but we phase directly with mcp/mcz.
    # Apply phase -1 iff all four clause ancillas are 1.
    qc.h(out)
    qc.mcx([c0, c1, c2, c3], out)
    qc.h(out)
    # The above computes out ^= AND(c0..c3) in phase kickback style? Instead use direct:
    # Actually simpler: apply multi-controlled Z on the clause ancillas.
    # Undo the h/mcx/h block since it modified out; replace with clean mcp phase.
    qc.h(out)
    qc.mcx([c0, c1, c2, c3], out)
    qc.h(out)

    # Direct multi-controlled phase: -1 when all clause ancillas == 1.
    qc.mcp(math.pi, [c0, c1, c2], c3)

    # Uncompute all clause ancillas (reverse order).
    for anc, lits in reversed(clauses):
        uncompute_clause(anc, lits)
