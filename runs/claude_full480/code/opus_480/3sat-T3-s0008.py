import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:10]   # one ancilla per clause
    out = ancilla_qubits[10]   # final phase ancilla

    # Each clause: (l0 OR l1 OR l2). Compute clause satisfaction into a clause ancilla.
    # For a literal that is "x_i" the qubit is 1 when true; for "NOT x_i" it is 1 when false.
    # Trick: clause is FALSE iff all three literals are false. We compute
    # clause_ancilla = OR(l0,l1,l2) using De Morgan:
    #   flip each qubit so that "literal false" becomes state 1 on that qubit line,
    #   then clause_ancilla = NOT(AND of those) . We instead compute the AND of
    #   (literal-false indicators) into the ancilla (=1 iff clause UNSAT), then flip.

    # clause spec: list of (var_index, negated?) ; negated True means literal is NOT x_i
    clauses = [
        [(0, True), (2, True), (5, True)],
        [(1, True), (4, False), (5, True)],
        [(1, True), (2, False), (6, True)],
        [(1, True), (3, True), (4, False)],
        [(3, False), (4, False), (5, True)],
        [(2, False), (5, True), (6, False)],
        [(2, False), (3, True), (5, False)],
        [(0, True), (4, False), (5, True)],
        [(1, True), (2, True), (4, False)],
        [(1, False), (4, True), (5, False)],
    ]

    def literal_false_controls(clause):
        # For each literal, the control qubit and whether we need it in state |1>
        # to represent "literal is false".
        # literal = x_i  -> false when x_i = 0 -> need control on |0> (open control)
        # literal = NOT x_i -> false when x_i = 1 -> need control on |1>
        ctrls = []
        for (i, neg) in clause:
            if neg:
                ctrls.append((x[i], 1))  # literal NOT x_i false when x_i=1
            else:
                ctrls.append((x[i], 0))  # literal x_i false when x_i=0
        return ctrls

    def compute_clause(anc, clause):
        # anc becomes 1 iff clause is SATISFIED.
        ctrls = literal_false_controls(clause)
        # Open-control mcx: flip x on qubits needing |0| control, apply ccx, flip back.
        for (q, val) in ctrls:
            if val == 0:
                qc.x(q)
        qc.mcx([c[0] for c in ctrls], anc)  # anc ^= (all literals false) = clause UNSAT
        for (q, val) in ctrls:
            if val == 0:
                qc.x(q)
        qc.x(anc)  # anc = NOT UNSAT = SAT

    # Compute all clause ancillas
    for k, clause in enumerate(clauses):
        compute_clause(cl[k], clause)

    # Phase: -1 iff all clause ancillas are 1 (formula satisfied)
    qc.h(out)
    qc.x(out)
    qc.mcx(cl, out)
    qc.x(out)
    qc.h(out)
    # Note: the H-X-mcx-X-H around out realizes a controlled-Z style phase kick.
    # Simpler: use multi-controlled Z via mcp(pi). Replace above block:
    # (kept mcx-based phase for clarity; net effect applies -1 when all cl==1)

    # Uncompute clause ancillas (mirror)
    for k in reversed(range(len(clauses))):
        clause = clauses[k]
        anc = cl[k]
        ctrls = literal_false_controls(clause)
        qc.x(anc)
        for (q, val) in ctrls:
            if val == 0:
                qc.x(q)
        qc.mcx([c[0] for c in ctrls], anc)
        for (q, val) in ctrls:
            if val == 0:
                qc.x(q)
