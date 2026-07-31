import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    # clause ancillas: one per clause (8), plus one final ancilla
    c = ancilla_qubits[:8]
    final = ancilla_qubits[8]

    # Each clause is an OR of 3 literals. clause is FALSE iff all literals false.
    # We compute clause_anc = OR(literals) into c[k].
    # literal True: variable qubit directly; literal NOT: negated qubit.
    # OR(a,b,c) = NOT(AND(NOT a, NOT b, NOT c)).
    # Implement: set c[k]=1 if any literal true.
    # Using: flip variable qubits so that "literal false" -> qubit=1, then
    # mcx of the three -> detects all-false; then X to make it "clause true".

    clauses = [
        [(1, True), (2, False), (5, True)],
        [(2, False), (3, False), (4, False)],
        [(3, True), (5, False), (6, False)],
        [(0, True), (4, False), (6, True)],
        [(2, False), (5, False), (7, True)],
        [(0, False), (3, False), (7, False)],
        [(4, False), (5, False), (6, True)],
        [(1, False), (4, True), (7, True)],
    ]

    def compute_clauses():
        for k, lits in enumerate(clauses):
            ctrls = []
            for (vi, pos) in lits:
                q = x[vi]
                # literal is FALSE when: pos and q==0, or (not pos) and q==1.
                # We want control-on-1 to mean "literal false".
                # If pos True: literal false when q==0 -> X then control.
                # If pos False (NOT): literal false when q==1 -> control directly.
                if pos:
                    qc.x(q)
                ctrls.append(q)
            # mcx: c[k] = 1 iff all three literals false (all ctrls==1)
            qc.mcx(ctrls, c[k])
            # c[k] now = "clause false". Flip to "clause true".
            qc.x(c[k])
            # restore variable qubits
            for (vi, pos) in lits:
                if pos:
                    qc.x(x[vi])

    def uncompute_clauses():
        for k in reversed(range(len(clauses))):
            lits = clauses[k]
            ctrls = []
            for (vi, pos) in lits:
                q = x[vi]
                if pos:
                    qc.x(q)
                ctrls.append(q)
            qc.x(c[k])
            qc.mcx(ctrls, c[k])
            for (vi, pos) in lits:
                if pos:
                    qc.x(x[vi])

    compute_clauses()
    # final = AND of all clause ancillas -> formula satisfied
    qc.mcx(c, final)
    qc.z(final)
    qc.mcx(c, final)
    uncompute_clauses()
