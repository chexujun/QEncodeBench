from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    p = problem_qubits
    a = ancilla_qubits

    # Clauses as lists of (var_index, is_positive) literals.
    # is_positive=True means literal is x_i; False means NOT x_i.
    clauses = [
        [(3, False), (5, False), (6, False)],
        [(2, False), (6, False), (7, False)],
        [(0, True),  (3, True),  (6, False)],
        [(1, False), (6, True),  (7, True)],
        [(2, False), (4, False), (6, True)],
        [(1, True),  (2, False), (5, False)],
        [(3, False), (4, True),  (5, True)],
    ]

    def clause_compute(clause, target):
        # Set target = OR of literals, using De Morgan on ancilla.
        # We compute NOT(clause) into target first (target becomes 1 iff clause false),
        # meaning target = AND of negated literals. Then target represents "clause unsatisfied".
        # For each literal l = (i, pos): literal is TRUE when qubit==pos.
        # clause is satisfied if any literal true. clause unsatisfied if all literals false.
        # literal false means qubit == (not pos).
        # We want an ancilla flag = 1 iff all literals false.
        # Prepare each control so that control==1 encodes "literal false".
        # literal false when qubit value == (0 if pos else 1).
        # If pos True: literal false when qubit==0 -> need X to make control 1.
        # If pos False: literal false when qubit==1 -> control already 1.
        ctrls = []
        for (i, pos) in clause:
            if pos:
                qc.x(p[i])
            ctrls.append(p[i])
        qc.mcx(ctrls, target)  # target = 1 iff all literals false (clause unsatisfied)
        # restore inputs
        for (i, pos) in clause:
            if pos:
                qc.x(p[i])

    # Compute per-clause "unsatisfied" flags into first 7 ancillas.
    for k, clause in enumerate(clauses):
        clause_compute(clause, a[k])

    # Formula satisfied iff NO clause unsatisfied, i.e. all a[0..6] == 0.
    # Apply phase -1 when all a[k]==0. Flip them, multi-controlled Z, flip back.
    flags = [a[k] for k in range(len(clauses))]
    for q in flags:
        qc.x(q)
    # multi-controlled Z on all flags: use mcp with pi.
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for q in flags:
        qc.x(q)

    # Uncompute the clause flags (mirror).
    for k in reversed(range(len(clauses))):
        clause_compute(clauses[k], a[k])
